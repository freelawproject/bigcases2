import environ

env = environ.FileAwareEnv()

COURTLISTENER_API_KEY = env("COURTLISTENER_API_KEY", default="")
