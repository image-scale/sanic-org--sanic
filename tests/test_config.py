import os
import pytest
from sanic import Sanic
from sanic.configuration import AppConfig


class TestConfigDefaults:
    def test_has_default_request_max_size(self):
        cfg = AppConfig()
        assert cfg["REQUEST_MAX_SIZE"] == 100_000_000

    def test_has_default_request_timeout(self):
        cfg = AppConfig()
        assert cfg["REQUEST_TIMEOUT"] == 60

    def test_has_default_keep_alive(self):
        cfg = AppConfig()
        assert cfg["KEEP_ALIVE"] is True

    def test_has_default_keep_alive_timeout(self):
        cfg = AppConfig()
        assert cfg["KEEP_ALIVE_TIMEOUT"] == 120

    def test_has_default_response_timeout(self):
        cfg = AppConfig()
        assert cfg["RESPONSE_TIMEOUT"] == 60

    def test_custom_defaults_override(self):
        cfg = AppConfig(defaults={"REQUEST_TIMEOUT": 30})
        assert cfg["REQUEST_TIMEOUT"] == 30


class TestConfigDictBehavior:
    def test_get_item(self):
        cfg = AppConfig()
        cfg["MY_KEY"] = "my_value"
        assert cfg["MY_KEY"] == "my_value"

    def test_get_with_default(self):
        cfg = AppConfig()
        assert cfg.get("NONEXISTENT", "fallback") == "fallback"

    def test_set_item(self):
        cfg = AppConfig()
        cfg["CUSTOM"] = 42
        assert cfg["CUSTOM"] == 42

    def test_iterate_keys(self):
        cfg = AppConfig(defaults={"A": 1, "B": 2})
        keys = list(cfg.keys())
        assert "A" in keys
        assert "B" in keys

    def test_attribute_access(self):
        cfg = AppConfig()
        cfg["MY_SETTING"] = "hello"
        assert cfg.MY_SETTING == "hello"

    def test_attribute_set(self):
        cfg = AppConfig()
        cfg.MY_SETTING = "world"
        assert cfg["MY_SETTING"] == "world"

    def test_attribute_error_for_missing(self):
        cfg = AppConfig()
        with pytest.raises(AttributeError):
            _ = cfg.TOTALLY_MISSING_KEY


class TestConfigEnvVars:
    def test_loads_sanic_prefixed_vars(self, monkeypatch):
        monkeypatch.setenv("SANIC_TEST_VALUE", "42")
        cfg = AppConfig()
        assert cfg["TEST_VALUE"] == 42

    def test_env_var_bool_conversion(self, monkeypatch):
        monkeypatch.setenv("SANIC_DEBUG", "true")
        cfg = AppConfig()
        assert cfg["DEBUG"] is True

    def test_env_var_false_bool(self, monkeypatch):
        monkeypatch.setenv("SANIC_FEATURE", "false")
        cfg = AppConfig()
        assert cfg["FEATURE"] is False

    def test_env_var_float_conversion(self, monkeypatch):
        monkeypatch.setenv("SANIC_RATE", "3.14")
        cfg = AppConfig()
        assert cfg["RATE"] == 3.14

    def test_env_var_string_kept(self, monkeypatch):
        monkeypatch.setenv("SANIC_NAME", "myapp")
        cfg = AppConfig()
        assert cfg["NAME"] == "myapp"

    def test_custom_prefix(self, monkeypatch):
        monkeypatch.setenv("MYAPP_LEVEL", "5")
        cfg = AppConfig(env_prefix="MYAPP_")
        assert cfg["LEVEL"] == 5

    def test_no_prefix_skips_env_loading(self):
        cfg = AppConfig(env_prefix="")
        assert isinstance(cfg, dict)


class TestConfigUpdateMethods:
    def test_update_from_dict(self):
        cfg = AppConfig()
        cfg.update({"CUSTOM_A": 1, "CUSTOM_B": "two"})
        assert cfg["CUSTOM_A"] == 1
        assert cfg["CUSTOM_B"] == "two"

    def test_update_from_object(self):
        class MySettings:
            DB_HOST = "localhost"
            DB_PORT = 5432
            _private = "skip"

        cfg = AppConfig()
        cfg.update_from_object(MySettings())
        assert cfg["DB_HOST"] == "localhost"
        assert cfg["DB_PORT"] == 5432
        assert "_private" not in cfg

    def test_update_config_with_dict(self):
        cfg = AppConfig()
        cfg.update_config({"X": 99})
        assert cfg["X"] == 99

    def test_update_config_with_object(self):
        class Obj:
            SETTING = "val"

        cfg = AppConfig()
        cfg.update_config(Obj())
        assert cfg["SETTING"] == "val"


class TestAppConfigIntegration:
    def test_app_has_config(self):
        app = Sanic("config_test")
        assert isinstance(app.config, AppConfig)
        Sanic._registry.pop("config_test", None)

    def test_app_config_attribute_access(self):
        app = Sanic("config_attr_test")
        app.config["MY_CUSTOM"] = "value"
        assert app.config.MY_CUSTOM == "value"
        Sanic._registry.pop("config_attr_test", None)

    def test_app_config_dict_access(self):
        app = Sanic("config_dict_test")
        app.config.SOMETHING = 123
        assert app.config["SOMETHING"] == 123
        Sanic._registry.pop("config_dict_test", None)

    def test_app_config_has_defaults(self):
        app = Sanic("config_defaults_test")
        assert app.config.REQUEST_MAX_SIZE == 100_000_000
        assert app.config.KEEP_ALIVE is True
        Sanic._registry.pop("config_defaults_test", None)
