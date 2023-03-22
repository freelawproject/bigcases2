import environ
from requests_oauthlib import OAuth1Session

env = environ.FileAwareEnv()

CONSUMER_KEY = env("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = env("TWITTER_CONSUMER_SECRET")
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
BASE_AUTHORIZATION_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"


def main():
    if not CONSUMER_KEY or not CONSUMER_SECRET:
        raise Exception(
            "Please check your env file and make sure TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET are set"
        )

    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET)

    try:
        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
    except ValueError:
        print(
            "There may have been an issue with the consumer_key or consumer_secret you entered."
        )

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")

    authorization_url = oauth.authorization_url(BASE_AUTHORIZATION_URL)
    print(f"Please go here and authorize: {authorization_url}")
    verifier = input("Paste the PIN here: ")

    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    print("\nAdd the following values in your .env file:")
    print(f"TWITTER_ACCESS_TOKEN={repr(access_token)}")
    print(f"TWITTER_ACCESS_TOKEN_SECRET={repr(access_token_secret)}")

    # Make the request
    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    fields = ""
    params = {"user.fields": fields}
    response = oauth.get("https://api.twitter.com/2/users/me", params=params)

    if response.status_code != 200:
        raise Exception(
            f"Request returned an error: {response.status_code} {response.text}"
        )

    data = response.json()["data"]

    print(
        "\nUse the admin panel to create a new channel with the following data:"
    )
    print("Service: Twitter")
    print(f"Account: {data['username']}")
    print(f"Account id: {data['id']}")
    print("Enable: True")


if __name__ == "__main__":
    main()
