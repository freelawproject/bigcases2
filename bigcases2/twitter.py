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

bp = Blueprint("twitter", __name__)

NGROK_ROOT = "https://efaf-2601-647-4c81-79f7-68c1-2edc-33b7-e78c.ngrok.io"
ENDPOINT = "/webhooks/twitter"
SECRETS = None
CONSUMER_SECRET = None


def load_secrets():
    global SECRETS, CONSUMER_SECRET
    if SECRETS is None:
        SECRETS_PATH = os.path.join(
            current_app.instance_path, "credentials.json"
        )
        with open(SECRETS_PATH, "r") as secrets_fp:
            SECRETS = json.load(secrets_fp)
        CONSUMER_SECRET = SECRETS[0]["api_key_secret"]
    return True


@click.command("twitter-test")
def twitter_test_command():
    """
    Tweet a test message and check push subscription.
    """
    pass


@bp.route(ENDPOINT, methods=["POST", "GET"])
def receive_webhook():
    current_app.logger.debug("Received a webhook request from Twitter.")
    current_app.logger.debug(f"Request: {request}")
    current_app.logger.debug(f"Request headers: {request.headers}")
    current_app.logger.debug(f"Request data: {request.data}")

    if request.method == "GET":
        current_app.logger.debug(
            "It's a GET request, so it's a CRC challenge."
        )

        load_secrets()

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
    load_secrets()
    url = f"https://api.twitter.com/1.1/account_activity/webhooks.json?url={NGROK_ROOT}{ENDPOINT}"
    current_app.logger.debug(f"url: {url}")

    token = SECRETS[0]["bearer_token"]
    # access_token = SECRETS[0]["access_token"]

    response = requests.post(
        url,
        headers={
            "authorization": f"bearer {token}",
            # "authorization": f"bearer {access_token}",
        },
    )
    current_app.logger.debug(response)
    current_app.logger.debug(response.status_code)
    current_app.logger.debug(response.headers)
    current_app.logger.debug(pformat(response.json()))


def init_app(app):
    # https://flask.palletsprojects.com/en/2.2.x/tutorial/database/#register-with-the-application
    app.cli.add_command(twitter_test_command)
    app.cli.add_command(register_webhook_command)
