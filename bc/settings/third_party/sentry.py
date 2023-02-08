import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration

env = environ.FileAwareEnv()
SENTRY_DSN = env("SENTRY_DSN", default="")
SENTRY_SAMPLE_TRACE = env("SENTRY_SAMPLE_TRACE", default=1.0)


if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            RedisIntegration(),
            RqIntegration(),
            DjangoIntegration(),
        ],
        ignore_errors=[KeyboardInterrupt],
        traces_sample_rate=SENTRY_SAMPLE_TRACE,
    )
