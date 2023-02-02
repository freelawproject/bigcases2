from .redis import REDIS_DATABASES, REDIS_HOST, REDIS_PORT

RQ_SHOW_ADMIN_LINK = True

RQ_QUEUES = {
    "default": {
        "URL": f"{REDIS_HOST}:{REDIS_PORT}",
        "DB": REDIS_DATABASES["QUEUE"],
    },
}
