import environ

from ..django import DEVELOPMENT
from ..third_party.aws import AWS_S3_CUSTOM_DOMAIN

env = environ.FileAwareEnv()

ALLOWED_HOSTS: list[str] = env("ALLOWED_HOSTS", default=["bots.law"])

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="THIS-is-a-Secret")

SECURE_HSTS_SECONDS = 63_072_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
CSP_CONNECT_SRC = ("'self'", "https://plausible.io/")
CSP_SCRIPT_SRC = ("'self'", AWS_S3_CUSTOM_DOMAIN, "https://plausible.io/")
CSP_DEFAULT_SRC = ("'self'", AWS_S3_CUSTOM_DOMAIN)


if DEVELOPMENT:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_DOMAIN = None
    # For debug_toolbar
    # INSTALLED_APPS.append('debug_toolbar')
    INTERNAL_IPS = ("127.0.0.1",)
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 9,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
