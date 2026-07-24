"""Development settings -- run with DJANGO_SETTINGS_MODULE=config.settings.dev"""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Relax the manifest storage so collectstatic isn't required during dev.
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
