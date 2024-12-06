import environ

env = environ.FileAwareEnv()

# Numbers of seconds the app should wait to process a webhook
WEBHOOK_DELAY_TIME = env.int("WEBHOOK_DELAY_TIME", default=120)

DOCTOR_HOST = env("DOCTOR_HOST", default="http://bc2-doctor:5050")

BANNER_ENABLED = env("BANNER_ENABLED", default=False)
