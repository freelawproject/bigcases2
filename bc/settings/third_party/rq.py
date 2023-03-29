import environ

env = environ.FileAwareEnv()

from .redis import REDIS_DATABASES, REDIS_HOST, REDIS_PORT

RQ_SHOW_ADMIN_LINK = True

RQ_QUEUES = {
    "default": {
        "URL": f"{REDIS_HOST}:{REDIS_PORT}",
        "DB": REDIS_DATABASES["QUEUE"],
    },
}

RQ_MAX_NUMBER_OF_RETRIES = env.int("RQ_MAX_NUMBER_OF_RETRIES", default=3)
RQ_RETRY_INTERVAL = env.int("RQ_RETRY_INTERVAL", default=20)
