import environ

env = environ.FileAwareEnv()

PACER_USERNAME = env("PACER_USERNAME", default="")
PACER_PASSWORD = env("PACER_PASSWORD", default="")
