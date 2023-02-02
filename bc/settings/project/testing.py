import sys

TESTING = "test" in sys.argv
if TESTING:
    PAGINATION_COUNT = 10
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
