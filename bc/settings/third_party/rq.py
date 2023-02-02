from .redis import REDIS_DATABASES, REDIS_HOST, REDIS_PORT

RQ_QUEUES = {
    "default": {
        "HOST": REDIS_HOST,
        "PORT": REDIS_PORT,
        "DB": REDIS_DATABASES["QUEUE"],
    },
}
