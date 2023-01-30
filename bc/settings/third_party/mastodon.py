import environ

env = environ.FileAwareEnv()


MASTODON_ACCOUNT = env("MASTODON_ACCOUNT",default="")
MASTODON_EMAIL = env("MASTODON_EMAIL",default="")
MASTODON_SERVER = env("MASTODON_SERVER", default="")
MASTODON_TOKEN = env("MASTODON_TOKEN",default="")

MASTODON_SHARED_KEY = env("MASTODON_SHARED_KEY", default="")
MASTODON_PUBLIC_KEY = env("MASTODON_PUBLIC_KEY", default="")
MASTODON_PRIVATE_KEY = env("MASTODON_PRIVATE_KEY", default="")
