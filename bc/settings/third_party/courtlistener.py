import environ

env = environ.FileAwareEnv()

COURTLISTENER_API_KEY = env("COURTLISTENER_API_KEY", default="")

CL_ALLOW_IPS = ["34.210.230.218", "54.189.59.91"]
