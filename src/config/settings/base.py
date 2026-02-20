import os
import sys
from pathlib import Path

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parents[2]  # /src
ROOT_DIR = BASE_DIR.parent  # /
PROJECT_NAME = config("PROJECT_NAME", default="NEWPROJECTNAME")


SECRET_KEY = config("SECRET_KEY")

CONFIGURATION = config("CONFIGURATION", default="dev")
if "test" in sys.argv:
    CONFIGURATION = "testing"

DEBUG = config("DEBUG", default=CONFIGURATION == "dev", cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*" if CONFIGURATION == "dev" else "", cast=Csv())
INTERNAL_IPS = config("INTERNAL_IPS", default="127.0.0.1", cast=Csv())

SITE_URL = config("SITE_URL", default="")

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default=SITE_URL, cast=Csv())

SENTRY_DSN = config("SENTRY_DSN", default="")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "polymorphic",
    # "anymail",
    "django_extensions",

    # Add the apps here
    "core",
    "accounts",
]


if SENTRY_DSN and SENTRY_DSN.strip() and SENTRY_DSN.strip().startswith(("http://", "https://")):
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    def strip_sensitive_data(event, hint):
        """Remove DisallowedHost errors from Sentry to avoid exceeding quota."""
        if "log_record" in hint and hint["log_record"].name == "django.security.DisallowedHost":
            return None
        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        before_send=strip_sensitive_data,
        send_default_pii=True,
    )


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.login_required_middleware",
]


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "config" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": config("POSTGRES_HOST", default="postgres"),
        "PORT": config("POSTGRES_PORT", default="5432"),
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER", default="postgres"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
    },
}

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us")

LANGUAGES = [
    ("en", "English"),
]

TIME_ZONE = config("TIME_ZONE", default="UTC")

USE_I18N = True

USE_L10N = True

USE_TZ = True

REDIS_URL = config("REDIS_URL")

WSGI_APPLICATION = "config.wsgi.application"
# ASGI_APPLICATION = "config.asgi.application"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = config("STATIC_ROOT", default="/data/staticfiles")

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "config", "static"),
)

MEDIA_URL = "/media/"
MEDIA_ROOT = config("MEDIA_ROOT", default="/data/media")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


KEY_PREFIX = config("KEY_PREFIX", default=PROJECT_NAME)
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BEAT_SCHEDULER = "redbeat.RedBeatScheduler"
# CELERYBEAT_SCHEDULE_FILENAME = config(
#     'CELERYBEAT_SCHEDULE_FILENAME', default='/data/celerybeat-schedule.db')
CELERY_BEAT_SCHEDULE = {}


DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@NEWPROJECTNAME.com")
EMAIL_BCC_ADDRESSES = config("EMAIL_BCC_ADDRESSES", default="", cast=Csv())

USE_HTTPS = False

LOGOUT_REDIRECT_URL = "/"

SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", default=604800, cast=int)  # 1 week in seconds by default

# Host for sending e-mail.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", default=25, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default="0", cast=bool)


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": KEY_PREFIX,
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
