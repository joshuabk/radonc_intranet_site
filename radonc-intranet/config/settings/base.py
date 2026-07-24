"""
Base settings shared by all environments.

Environment-specific settings live in dev.py and prod.py.
Secrets and machine-specific values are read from environment
variables (see .env.example at the project root).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def env(key: str, default=None):
    """Small helper so settings read cleanly without extra dependencies."""
    return os.environ.get(key, default)


def env_bool(key: str, default: bool = False) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def env_list(key: str, default: str = "") -> list[str]:
    raw = os.environ.get(key, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


SECRET_KEY = env("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")

DEBUG = False  # overridden in dev.py

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

SITE_NAME = env("SITE_NAME", "Radiation Oncology Intranet")
ORG_NAME = env("ORG_NAME", "Hospital System")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

# Local feature apps. To add a new large feature to the site, create a new
# app under apps/ and append it here -- see docs/ADDING_FEATURES.md.
LOCAL_APPS = [
    "apps.core",
    "apps.linkhub",
    "apps.contacts",
    "apps.coverage",
    "apps.huddle",
    "apps.reporting",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Entire intranet requires login by default. Views can opt out with
    # @login_not_required (django.contrib.auth.decorators).
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Exposes the feature registry (nav + home cards) and site
                # branding to every template.
                "apps.core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Databases
#
# "default" is the intranet's own application database.
#
# Read-only connections to clinical system databases (ARIA, MOSAIQ) are
# configured here but DISABLED until credentials are provided. The reporting
# app routes its queries through apps.reporting.datasources, which checks
# whether these aliases are configured before running anything.
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

# Example ARIA (Varian) read-only reporting connection -- SQL Server.
# Requires: pip install mssql-django pyodbc, plus the ODBC driver.
if env("ARIA_DB_HOST"):
    DATABASES["aria"] = {
        "ENGINE": "mssql",
        "HOST": env("ARIA_DB_HOST"),
        "PORT": env("ARIA_DB_PORT", "1433"),
        "NAME": env("ARIA_DB_NAME", "VARIAN"),
        "USER": env("ARIA_DB_USER"),
        "PASSWORD": env("ARIA_DB_PASSWORD"),
        "OPTIONS": {"driver": "ODBC Driver 18 for SQL Server",
                    "extra_params": "ApplicationIntent=ReadOnly;TrustServerCertificate=yes"},
    }

# Example MOSAIQ (Elekta) read-only reporting connection -- SQL Server.
if env("MOSAIQ_DB_HOST"):
    DATABASES["mosaiq"] = {
        "ENGINE": "mssql",
        "HOST": env("MOSAIQ_DB_HOST"),
        "PORT": env("MOSAIQ_DB_PORT", "1433"),
        "NAME": env("MOSAIQ_DB_NAME", "MOSAIQ"),
        "USER": env("MOSAIQ_DB_USER"),
        "PASSWORD": env("MOSAIQ_DB_PASSWORD"),
        "OPTIONS": {"driver": "ODBC Driver 18 for SQL Server",
                    "extra_params": "ApplicationIntent=ReadOnly;TrustServerCertificate=yes"},
    }

DATABASE_ROUTERS = ["apps.reporting.routers.ClinicalSystemRouter"]

# ---------------------------------------------------------------------------
# Authentication
#
# Default: Django's local accounts (good for the pilot).
# For production on a hospital network you will almost certainly bind this
# to Active Directory via LDAP -- see docs/AUTHENTICATION.md for a worked
# django-auth-ldap example.
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "login"

# Named groups used for authorization across the site.
# Created automatically by `manage.py bootstrap_site`.
SITE_GROUPS = {
    "PHYSICS": "Physics",
    "DOSIMETRY": "Dosimetry",
    "THERAPISTS": "Therapists",
    "REPORTING": "Reporting Access",
    "CONTENT_ADMINS": "Content Admins",
}

# ---------------------------------------------------------------------------
# I18N / static files
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", "America/New_York")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Logging -- console plus a rotating file, useful on an internal server.
# ---------------------------------------------------------------------------
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "{asctime} {levelname} {name} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "intranet.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "standard",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
}
