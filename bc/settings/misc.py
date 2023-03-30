import environ

env = environ.FileAwareEnv()

# Numbers of seconds the app should wait to process a webhook
WEBHOOK_DELAY_TIME = env.int("WEBHOOK_DELAY_TIME", default=120)

DOCTOR_HOST = env("DOCTOR_HOST", default="http://bc-doctor:5050")
