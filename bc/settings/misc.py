import environ

env = environ.FileAwareEnv()

# Numbers of seconds the app should wait to process a webhook
WEBHOOK_DELAY_TIME = env.int("WEBHOOK_DELAY_TIME", default=120)

DOCTOR_HOST = env("DOCTOR_HOST", default="http://bc2-doctor:5050")
# Sent as "Authorization: Bearer <token>" on every doctor request. Doctor
# ignores the header until its own DOCTOR_AUTH_TOKENS is set, so this can
# be deployed first; blank sends nothing.
DOCTOR_AUTH_TOKEN = env("DOCTOR_AUTH_TOKEN", default="")
