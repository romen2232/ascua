"""Settings shared by every environment."""

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("ASCUA_SECRET_KEY", "")
DEBUG = False
ALLOWED_HOSTS: list[str] = [h for h in os.environ.get("ASCUA_ALLOWED_HOSTS", "").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "drf_spectacular",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "axes",
    "rest_framework_simplejwt.token_blacklist",
    "shared_kernel.infrastructure.apps.SharedKernelConfig",
    "identity.infrastructure.apps.IdentityConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "axes.middleware.AxesMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Lock out an email + IP pair for 15 minutes after 5 failed passwords.
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_CALLABLE = "identity.infrastructure.credentials.lockout_response"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "USER_ID_FIELD": "id",
    "UPDATE_LAST_LOGIN": False,
}

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# The runtime connects as ascua_app, which cannot bypass row-level security.
# Migrations run with ASCUA_DB_USER=ascua_owner.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("ASCUA_DB_NAME", "ascua"),
        "USER": os.environ.get("ASCUA_DB_USER", "ascua_app"),
        "PASSWORD": os.environ.get("ASCUA_DB_PASSWORD", ""),
        "HOST": os.environ.get("ASCUA_DB_HOST", "localhost"),
        "PORT": os.environ.get("ASCUA_DB_PORT", "5432"),
        "ATOMIC_REQUESTS": True,
    }
}

AUTH_USER_MODEL = "identity.UserRecord"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "es"
USE_I18N = True
USE_TZ = True
TIME_ZONE = "UTC"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "EXCEPTION_HANDLER": "shared_kernel.api.errors.exception_handler",
    "UNAUTHENTICATED_USER": None,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ascua API",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
SYSTEM_QUERY_ALLOWLIST: list[str] = []

OTP_TOTP_ISSUER = "ascua"
