import socket
from typing import Any

import environ
from csp.constants import NONE, REPORT_SAMPLE, SELF

from bc.settings.django import DEVELOPMENT, INSTALLED_APPS
from bc.settings.project.testing import TESTING
from bc.settings.third_party.aws import AWS_S3_CUSTOM_DOMAIN

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

# PERMISSIONS_POLICY
# Dictionary to disable many potentially privacy-invading and annoying features
# for all scripts:
PERMISSIONS_POLICY: dict[str, list[str]] = {
    "browsing-topics": [],
}

# CSP
# Components:
# - hCaptcha: https://docs.hcaptcha.com/#content-security-policy-settings
# - Plausible: https://github.com/plausible/docs/issues/20
CONTENT_SECURITY_POLICY: dict[str, Any] = {
    "DIRECTIVES": {
        "base-uri": [NONE],
        "connect-src": [
            SELF,
            "https://hcaptcha.com/",
            "https://*.hcaptcha.com/",
            "https://plausible.io/",
        ],
        "default-src": [
            SELF,
            f"https://{AWS_S3_CUSTOM_DOMAIN}/",
        ],
        "font-src": [
            SELF,
            f"https://{AWS_S3_CUSTOM_DOMAIN}/",
            "data:",  # Some browser extensions like this.
        ],
        "frame-src": [
            SELF,
            "https://hcaptcha.com/",
            "https://*.hcaptcha.com/",
        ],
        "img-src": [
            SELF,
            f"https://{AWS_S3_CUSTOM_DOMAIN}/",
            "data:",  # @tailwindcss/forms uses data URIs for images.
        ],
        "object-src": [NONE],
        "script-src": [
            SELF,
            REPORT_SAMPLE,
            f"https://{AWS_S3_CUSTOM_DOMAIN}/",
            "https://hcaptcha.com/",
            "https://*.hcaptcha.com/",
            "https://plausible.io/",
        ],
        "style-src": [
            SELF,
            REPORT_SAMPLE,
            f"https://{AWS_S3_CUSTOM_DOMAIN}/",
            "https://hcaptcha.com/",
            "https://*.hcaptcha.com/",
        ],
    },
}
if not any(
    (DEVELOPMENT, TESTING)
):  # Development and test aren’t used over HTTPS (yet)
    CONTENT_SECURITY_POLICY["DIRECTIVES"]["upgrade-insecure-requests"] = True


RATELIMIT_VIEW = "bc.web.views.ratelimited"

if DEVELOPMENT:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_DOMAIN = None
    # For debug_toolbar
    if not TESTING:
        INSTALLED_APPS = [
            *INSTALLED_APPS,
            "debug_toolbar",
        ]

    # Get the list of IPv4 addresses for the interface on the same host. If you want to know more
    # about this, you can check the following links:
    #   https://github.com/freelawproject/bigcases2/pull/210#discussion_r1182078837
    #   https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#configure-internal-ips
    try:
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS = [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips] + [
            "127.0.0.1"
        ]
    except (
        socket.gaierror
    ):  # this is needed as the pre-commit mypy check fails here
        INTERNAL_IPS = ["127.0.0.1"]
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
