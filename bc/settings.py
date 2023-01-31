from pathlib import Path

import environ

env = environ.FileAwareEnv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="THIS-is-a-Secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS: list[str] = env("ALLOWED_HOSTS", default=["*"])

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
    "bc.subscription",
    "bc.web",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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
        "NAME": env("DB_NAME", default="bigcases2"),
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

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
COURTLISTENER_API_KEY = env("COURTLISTENER_API_KEY", default="")

HOSTNAME = env("HOSTNAME", default="")

MASTODON_ACCOUNT = env("MASTODON_ACCOUNT", default="")
MASTODON_EMAIL = env("MASTODON_EMAIL", default="")
MASTODON_SERVER = env("MASTODON_SERVER", default="")
MASTODON_TOKEN = env("MASTODON_TOKEN", default="")

MASTODON_SHARED_KEY = env("MASTODON_SHARED_KEY", default="")
MASTODON_PUBLIC_KEY = env("MASTODON_PUBLIC_KEY", default="")
MASTODON_PRIVATE_KEY = env("MASTODON_PRIVATE_KEY", default="")
