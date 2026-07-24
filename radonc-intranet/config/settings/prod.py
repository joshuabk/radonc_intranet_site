"""
Production settings for the internal hospital network.

Run with DJANGO_SETTINGS_MODULE=config.settings.prod and provide:
  DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS, and (recommended) a real
  database via the *_DB_* environment variables.
"""
from .base import *  # noqa: F401,F403
from .base import env, env_bool, env_list

DEBUG = False

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# Internal sites are often served over HTTP behind the firewall at first.
# Flip INTRANET_HTTPS=true once a certificate is in place (recommended).
if env_bool("INTRANET_HTTPS", False):
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30

SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Recommended production application database (PostgreSQL on the intranet
# server). Falls back to SQLite if not configured, which is fine for a pilot.
if env("APP_DB_NAME"):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("APP_DB_NAME"),
        "USER": env("APP_DB_USER"),
        "PASSWORD": env("APP_DB_PASSWORD"),
        "HOST": env("APP_DB_HOST", "localhost"),
        "PORT": env("APP_DB_PORT", "5432"),
    }
