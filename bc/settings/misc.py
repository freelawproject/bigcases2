import environ

env = environ.FileAwareEnv()

WEBHOOK_DELAY_TIME = env.int("WEBHOOK_DELAY_TIME", default=120)