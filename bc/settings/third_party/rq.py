import environ

from bc.settings.project.testing import TESTING

from .redis import REDIS_DATABASES, REDIS_HOST, REDIS_PORT

env = environ.FileAwareEnv()

RQ_SHOW_ADMIN_LINK = True

RQ_QUEUES = {
    "default": {
        "URL": f"{REDIS_HOST}:{REDIS_PORT}",
        "DB": REDIS_DATABASES["QUEUE"],
    },
}

RQ_MAX_NUMBER_OF_RETRIES: int = env.int("RQ_MAX_NUMBER_OF_RETRIES", default=3)
RQ_RETRY_INTERVAL: int = env.int("RQ_RETRY_INTERVAL", default=20)
RQ_POST_RETRY_INTERVALS: list[int] = env.list(
    "RQ_POST_RETRY_INTERVALS", cast=int, default=[20, 60, 120]
)

if TESTING:
    for queueConfig in RQ_QUEUES.values():
        queueConfig["ASYNC"] = False
