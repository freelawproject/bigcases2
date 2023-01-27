import base64

import environ
from mastodon import Mastodon

env = environ.FileAwareEnv()

MASTODON_SERVER = env("MASTODON_SERVER")
MASTODON_TOKEN = env("MASTODON_TOKEN")


def main():
    mastodon = Mastodon(
        api_base_url=MASTODON_SERVER,
        access_token=MASTODON_TOKEN,
    )

    priv_dict, pub_dict = mastodon.push_subscription_generate_keys()

    shared_key = base64.encodebytes(priv_dict["auth"]).decode("utf-8").strip()
    public_key = base64.encodebytes(pub_dict["pubkey"]).decode("utf-8").strip()
    private_key = priv_dict["privkey"]

    print("Add the following values in your .env file:")
    print(f"MASTODON_SHARED_KEY={repr(shared_key)}")
    print(f"MASTODON_PUBLIC_KEY={repr(public_key)}")
    print(f"MASTODON_PRIVATE_KEY={repr(private_key)}")


if __name__ == "__main__":
    main()
