import environ

env = environ.FileAwareEnv()

TWITTER_API_KEY = env("TWITTER_API_KEY", default="")
TWITTER_API_SECRET = env("TWITTER_API_SECRET", default="")
TWITTER_ACCESS_TOKEN = env("TWITTER_ACCESS_TOKEN", default="")
TWITTER_ACCESS_TOKEN_SECRET = env("TWITTER_ACCESS_TOKEN_SECRET", default="")
