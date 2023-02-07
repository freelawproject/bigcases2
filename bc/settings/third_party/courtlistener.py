import environ

env = environ.FileAwareEnv()

COURTLISTENER_API_KEY = env("COURTLISTENER_API_KEY", default="")

COURTLISTENER__ALLOW_IPS = ["34.210.230.218", "54.189.59.91"]
