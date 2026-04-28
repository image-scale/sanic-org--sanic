"""Pages package."""
from sanic.pages.base import BasePage
from sanic.pages.error import ErrorPage
from sanic.pages.directory_page import DirectoryPage


__all__ = [
    "BasePage",
    "ErrorPage",
    "DirectoryPage",
]
