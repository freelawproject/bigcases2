import environ

env = environ.FileAwareEnv()


REDIS_HOST = env("REDIS_HOST", default="bc2-redis")
REDIS_PORT = env("REDIS_PORT", default=6379)

REDIS_DATABASES = {
    "QUEUE": 0,
    "CACHE": 1,
}