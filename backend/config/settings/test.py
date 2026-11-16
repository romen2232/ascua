"""Test settings.

The test runner connects as ascua_owner so it can create the test database and run migrations;
tests/conftest.py then drops every connection to ascua_app with SET ROLE, so tests exercise
row-level security exactly as the running app does.
"""

import os

from .base import *  # noqa: F403
from .base import DATABASES

SECRET_KEY = "test-only-insecure-key"
ALLOWED_HOSTS = ["testserver"]

DATABASES["default"].update(
    {
        "USER": "ascua_owner",
        "PASSWORD": os.environ.get("ASCUA_DB_PASSWORD", "ascua_owner"),
        "PORT": os.environ.get("ASCUA_DB_PORT", "5442"),
    }
)

PASSWORD_HASHERS = ["django.contrib.auth.hashers.Argon2PasswordHasher"]
