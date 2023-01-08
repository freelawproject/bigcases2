"""
Twitter webhooks & stuff
"""

import os
import json
import hmac
import hashlib
import base64
from pprint import pformat

from flask import (
    Blueprint,
    request,
    current_app,
    g,
)
import click
import requests
from twitter import Twitter, OAuth

bp = Blueprint("twitter", __name__)

NGROK_ROOT = "https://efaf-2601-647-4c81-79f7-68c1-2edc-33b7-e78c.ngrok.io"
ENDPOINT = "/webhooks/twitter"
MAIN_ACCOUNT = "bcb2-dev"
SECRETS = None


def load_secrets():
    global SECRETS
    SECRETS_PATH = os.path.join(current_app.instance_path, "credentials2.json")
    with open(SECRETS_PATH, "r") as secrets_fp:
        SECRETS = json.load(secrets_fp)
    return SECRETS


@click.command("twitter-test")
def twitter_test_command():
    """
    Tweet a test message and check push subscription.
    """
    pass


@click.command("twitter-post")
@click.argument("account")
def twitter_post_command(account):
    """
    Send a Tweet.
    """
    get_twitter(account)
    result = g.twitter.statuses.update(status="Hello, world!")
    current_app.logger.info(result)


@bp.route(ENDPOINT, methods=["POST", "GET"])
def receive_webhook():
    current_app.logger.debug("Received a webhook request from Twitter.")
    current_app.logger.debug(f"Request: {request}")
    current_app.logger.debug(f"Request headers: {request.headers}")
    current_app.logger.debug(f"Request data: {request.data}")

    if not SECRETS:
        load_secrets()

    if request.method == "GET":
        current_app.logger.debug(
            "It's a GET request, so it's a CRC challenge."
        )

        load_secrets()
        CONSUMER_SECRET = SECRETS["twitter"][MAIN_ACCOUNT]["api_key_secret"]

        # CRC: https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/guides/securing-webhooks
        crc_token = request.headers.get("crc_token")

        # creates HMAC SHA-256 hash from incomming token and your consumer secret
        sha256_hash_digest = hmac.new(
            CONSUMER_SECRET, msg=crc_token, digestmod=hashlib.sha256
        ).digest()

        # construct response data with base64 encoded hash
        response = {
            "response_token": "sha256=" + base64.b64encode(sha256_hash_digest)
        }

        current_app.logger.debug(f"Response: {response}")

        # returns properly formatted json response
        return response

    else:
        # POST
        # TODO

        # TODO: Check x-twitter-webhooks-signature header
        # https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/guides/securing-webhooks

        return {
            "status": "ok",
        }


@click.command("twitter-register")
def register_webhook_command():
    """
    Register a webhook with Twitter
    """
    if not SECRETS:
        load_secrets()
    url = f"https://api.twitter.com/1.1/account_activity/webhooks.json?url={NGROK_ROOT}{ENDPOINT}"
    current_app.logger.debug(f"url: {url}")

    token = SECRETS["twitter"][MAIN_ACCOUNT]["bearer_token"]

    response = requests.post(
        url,
        headers={
            "authorization": f"bearer {token}",
        },
    )
    current_app.logger.debug(response)
    current_app.logger.debug(response.status_code)
    current_app.logger.debug(response.headers)
    current_app.logger.debug(pformat(response.json()))


def get_twitter(account=None):
    current_app.logger.debug(f"get_twitter(): called with account={account}")
    if not SECRETS:
        load_secrets()
    t = Twitter(
        auth=OAuth(
            SECRETS["twitter"].get(account).get("access_token"),
            SECRETS["twitter"].get(account).get("access_token_secret"),
            SECRETS["twitter"].get(MAIN_ACCOUNT).get("api_key"),
            SECRETS["twitter"].get(MAIN_ACCOUNT).get("api_key_secret"),
        )
    )
    g.twitter = t
    current_app.logger.debug(g.twitter)
    return g.twitter


def init_app(app):
    # https://flask.palletsprojects.com/en/2.2.x/tutorial/database/#register-with-the-application
    app.cli.add_command(twitter_test_command)
    app.cli.add_command(register_webhook_command)
    app.cli.add_command(twitter_post_command)
