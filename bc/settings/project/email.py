import environ

env = environ.FileAwareEnv()
DEVELOPMENT = env.bool("DEVELOPMENT", default=True)

if DEVELOPMENT:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django_ses.SESBackend"
    AWS_SES_REGION_NAME = "us-west-2"
    AWS_SES_REGION_ENDPOINT = "email.us-west-2.amazonaws.com"


DEFAULT_FROM_EMAIL = "Bots.law <noreply@bots.law>"
LOW_FUNDING_EMAIL_THRESHOLDS = env.list(
    "LOW_FUNDING_EMAIL_THRESHOLDS", cast=float, default=[75.0, 40.0, 3.0]
)
