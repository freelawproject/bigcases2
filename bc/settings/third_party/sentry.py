import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

env = environ.FileAwareEnv()
SENTRY_DSN = env("SENTRY_DSN", default="")
SENTRY_SAMPLE_TRACE = env("SENTRY_SAMPLE_TRACE", default=1.0)

# IA's library logs a lot of errors, which get sent to sentry unnecessarily
ignore_logger("internetarchive.session")
ignore_logger("internetarchive.item")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        ignore_errors=[KeyboardInterrupt],
        traces_sample_rate=SENTRY_SAMPLE_TRACE,
    )
