import socket

import environ

from ..django import DEVELOPMENT, INSTALLED_APPS
from ..third_party.aws import AWS_S3_CUSTOM_DOMAIN
from ..third_party.sentry import SENTRY_REPORT_URI

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
CSP_IMG_SRC = (
    "'self'",
    AWS_S3_CUSTOM_DOMAIN,
    "https://plausible.io/",
    "data:",  # @tailwindcss/forms uses data URIs for images.
)
CSP_SCRIPT_SRC = (
    "'self'",
    AWS_S3_CUSTOM_DOMAIN,
    "https://plausible.io/",
    "https://hcaptcha.com/",
)
CSP_DEFAULT_SRC = (
    "'self'",
    AWS_S3_CUSTOM_DOMAIN,
    "https://newassets.hcaptcha.com/",
)
if SENTRY_REPORT_URI:
    CSP_REPORT_URI = SENTRY_REPORT_URI


RATELIMIT_VIEW = "bc.web.views.ratelimited"

if DEVELOPMENT:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_DOMAIN = None
    # For debug_toolbar
    INSTALLED_APPS.append("debug_toolbar")

    # Get the list of IPv4 addresses for the interface on the same host. If you want to know more
    # about this, you can check the following links:
    #   https://github.com/freelawproject/bigcases2/pull/210#discussion_r1182078837
    #   https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#configure-internal-ips
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips] + [
        "127.0.0.1"
    ]
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
