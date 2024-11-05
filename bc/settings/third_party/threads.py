import environ

env = environ.FileAwareEnv()

THREADS_APP_ID = env("THREADS_APP_ID", default="")
THREADS_APP_SECRET = env("THREADS_APP_SECRET", default="")
THREADS_CALLBACK_URL = env("THREADS_CALLBACK_URL", default="")
