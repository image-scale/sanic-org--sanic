#!/bin/bash
set -eo pipefail
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export CI=true

cd /workspace/sanic
pytest -v --tb=short --no-cov -p no:cacheprovider -n 3 --dist loadgroup \
    --ignore=tests/http3 \
    --deselect=tests/test_daemon.py::test_validate_writable_dir_not_writable \
    --deselect="tests/test_http_alt_svc.py::test_http1_response_has_alt_svc" \
    "--deselect=tests/test_response_file.py::test_guess_content_type[test.js-text/javascript; charset=utf-8]" \
    tests/

