"""
Twitter is garbage
"""

import json
from pprint import pprint

import requests
from authlib.integrations.requests_client import OAuth1Session

status_url = "https://api.twitter.com/1.1/statuses/update.json"
request_token_url = "https://api.twitter.com/oauth/request_token"
authenticate_url = "https://api.twitter.com/oauth/authenticate"
access_token_url = "https://api.twitter.com/oauth/access_token"
verify_url = "https://api.twitter.com/1.1/account/verify_credentials.json"

creds_path = "instance/credentials.json"
creds = json.load(open(creds_path))
app_creds = creds[0]
big_cases_test_creds = creds[1]


def do_oauth1():
    # Initialize OAuth 1.0 Client
    # https://docs.authlib.org/en/latest/client/oauth1.html#initialize-oauth-1-0-client
    print("# Initialize OAuth 1.0 Client")
    the_creds = app_creds
    client = OAuth1Session(
        the_creds.get("api_key"),
        the_creds.get("api_key_secret"),
    )

    # Fetch Temporary Credential
    # https://docs.authlib.org/en/latest/client/oauth1.html#fetch-temporary-credential
    print("# Fetch Temporary Credential")
    # client.redirect_uri = "https://example.com/twitter"
    client.redirect_uri = "oob"
    request_token = client.fetch_request_token(request_token_url)
    print(request_token)

    # Redirect to Authorization Endpoint
    # https://docs.authlib.org/en/latest/client/oauth1.html#redirect-to-authorization-endpoint
    print("# Redirect to Authorization Endpoint")
    authorization_url = client.create_authorization_url(
        authenticate_url, request_token["oauth_token"]
    )
    print("Now go visit this URL to authorize the app:")
    print(authorization_url)
    print()

    # Fetch Access Token
    # https://docs.authlib.org/en/latest/client/oauth1.html#fetch-access-token
    print("# Fetch Access Token")
    verifier = input("Input PIN: ")
    token_dict = client.fetch_access_token(access_token_url, verifier)
    pprint(token_dict)

    print("# Verify")
    resp = client.get(verify_url)
    pprint(resp.json())


if __name__ == "__main__":
    do_oauth1()
