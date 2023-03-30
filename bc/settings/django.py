from pathlib import Path

import environ

from .project.testing import TESTING
from .third_party.redis import REDIS_DATABASES, REDIS_HOST, REDIS_PORT

env = environ.FileAwareEnv()

DEVELOPMENT = env.bool("DEVELOPMENT", default=True)

HOSTNAME = env("HOSTNAME", default="localhost:8888")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parents[2]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

TEMPLATE_ROOT = BASE_DIR / "bc/assets/templates/"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bc.core",
    "bc.users",
    "bc.channel",
    "bc.sponsorship",
    "bc.subscription",
    "bc.web",
    # other apps
    "django_rq",
    "tailwind",
]

if DEVELOPMENT:
    INSTALLED_APPS.append("django_browser_reload")

TAILWIND_APP_NAME = "bc.web"

INTERNAL_IPS = ("127.0.0.1",)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

if DEVELOPMENT:
    MIDDLEWARE.append(
        "django_browser_reload.middleware.BrowserReloadMiddleware"
    )

ROOT_URLCONF = "bc.urls"
AUTH_USER_MODEL = "users.User"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_ROOT],
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

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="bots"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="postgres"),
        "CONN_MAX_AGE": env("DB_CONN_MAX_AGE", default=0),
        "HOST": env("DB_HOST", default="bc2-postgresql"),
        # Disable DB serialization during tests for small speed boost
        "TEST": {"SERIALIZE": False},
        "OPTIONS": {
            # See: https://www.postgresql.org/docs/current/libpq-ssl.html#LIBPQ-SSL-PROTECTION
            # "prefer" is fine in dev, but poor in prod, where it should be
            # "require" or above.
            "sslmode": env("DB_SSL_MODE", default="prefer"),
        },
    },
}

####################
# Cache & Sessions #
####################
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"{REDIS_HOST}:{REDIS_PORT}",
        "OPTIONS": {"db": REDIS_DATABASES["CACHE"]},
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = env.str("STATIC_URL", default="static/")
STATICFILES_DIRS = (BASE_DIR / "bc/assets/static-global/",)
STATIC_ROOT = BASE_DIR / "bc/assets/static/"

if not any([TESTING, DEBUG]):
    STATICFILES_STORAGE = (
        "bc.core.utils.storage.SubDirectoryS3ManifestStaticStorage"
    )

LOGIN_URL = "/sign-in/"
LOGIN_REDIRECT_URL = "/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
