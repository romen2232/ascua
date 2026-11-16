"""Local development settings."""

import os

from .base import *  # noqa: F403
from .base import DATABASES

DEBUG = True
SECRET_KEY = os.environ.get("ASCUA_SECRET_KEY", "dev-only-insecure-key-0123456789abcdef")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES["default"].update(
    {
        "PORT": os.environ.get("ASCUA_DB_PORT", "5442"),
        "PASSWORD": os.environ.get("ASCUA_DB_PASSWORD", DATABASES["default"]["USER"]),
    }
)
