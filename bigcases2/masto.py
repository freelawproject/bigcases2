"""
Mastodon webhook & related functions
Called "masto" to avoid name collision with Mastodon.py package ("mastodon").

Mastodon documentation: https://docs.joinmastodon.org/methods/push/
Push Web API documentation: https://developer.mozilla.org/en-US/docs/Web/API/Push_API
Mastdon.py documentation: https://mastodonpy.readthedocs.io/en/stable/#push-subscriptions
"""
import json
import os
import base64
from pprint import pformat, pprint
from copy import copy

from flask import (
    Blueprint,
    request,
    current_app,
    g,
)
import click
from mastodon import Mastodon, MastodonNotFoundError

from bigcases2.db import get_db

bp = Blueprint("mastodon", __name__)


def get_mastodon():
    if "mastodon" not in g:
        g.mastodon = Mastodon(
            api_base_url=current_app.config["MASTODON"]["SERVER"],
            # client_id=current_app.config["MASTODON"]["KEY"],
            # client_secret=current_app.config["MASTODON"]["SECRET"],
            access_token=current_app.config["MASTODON"]["TOKEN"],
        )
        current_app.logger.debug(f"Created Mastodon instance: {g.mastodon}")
    return g.mastodon


def get_keys():
    # Restore keys
    if "mastodon_priv_dict" not in g or "mastodon_pub_dict" not in g:
        current_app.logger.debug("get_keys(): keys not in g")
        priv_fn = os.path.join(current_app.instance_path, "mastodon_priv.json")
        pub_fn = os.path.join(current_app.instance_path, "mastodon_pub.json")
        if not os.path.exists(priv_fn) or not os.path.exists(pub_fn):
            current_app.logger.debug("get_keys(): didn't find key JSON files")
            subscribe()
        else:
            current_app.logger.debug("get_keys(): found key JSON files")
            with open(priv_fn, "r") as priv_f:
                priv_dict = json.load(priv_f)
                # base64-decode the "auth" part
                priv_dict["auth"] = base64.b64decode(priv_dict["auth"])
                g.mastodon_priv_dict = priv_dict
            with open(pub_fn, "r") as pub_f:
                pub_dict = json.load(pub_f)
                # base64-decode the "auth" part
                pub_dict["auth"] = base64.b64decode(pub_dict["auth"])
                pub_dict["pubkey"] = base64.b64decode(pub_dict["pubkey"])
                g.mastodon_pub_dict = pub_dict

            current_app.logger.debug(
                "get_keys(): loaded keys from key JSON files"
            )

    return g.mastodon_priv_dict, g.mastodon_pub_dict


@bp.route("/webhooks/mastodon", methods=["POST"])
def receive_push():
    current_app.logger.debug("Received a push webhook from Mastodon.")
    current_app.logger.debug(f"Request: {request}")
    current_app.logger.debug(f"Request headers: {request.headers}")
    current_app.logger.debug(f"Request data: {request.data}")

    m = get_mastodon()
    priv_dict, pub_dict = get_keys()
    push = m.push_subscription_decrypt_push(
        data=request.data,
        decrypt_params=priv_dict,
        encryption_header=request.headers.get("Encryption"),
        crypto_key_header=request.headers.get("Crypto-Key"),
    )
    current_app.logger.debug(f"push: {push}")

    return {
        "status": "ok",
    }


def subscribe(force=False):
    m = get_mastodon()

    # Generate keys
    if "mastodon_priv_dict" not in g or "mastodon_pub_dict" not in g or force:
        priv_fn = os.path.join(current_app.instance_path, "mastodon_priv.json")
        pub_fn = os.path.join(current_app.instance_path, "mastodon_pub.json")
        priv_dict, pub_dict = m.push_subscription_generate_keys()
        g.mastodon_priv_dict = priv_dict
        g.mastodon_pub_duct = pub_dict

        # Write key JSON files

        # Need to base64-encode the "auth" and "pubkey" parts first
        priv_copy = copy(priv_dict)
        pub_copy = copy(pub_dict)
        priv_copy["auth"] = (
            base64.encodebytes(priv_copy["auth"]).decode("utf-8").strip()
        )
        pub_copy["auth"] = (
            base64.encodebytes(pub_copy["auth"]).decode("utf-8").strip()
        )
        pub_copy["pubkey"] = (
            base64.encodebytes(pub_copy["pubkey"]).decode("utf-8").strip()
        )

        # Now write the files
        with open(priv_fn, "w") as priv_f:
            json.dump(priv_copy, priv_f, indent=4)
        with open(pub_fn, "w") as pub_f:
            json.dump(pub_copy, pub_f, indent=4)

    # Send subscribe request
    self_url = current_app.config.get("SELF_URL")
    endpoint = f"{self_url}/webhooks/mastodon"
    response = m.push_subscription_set(
        endpoint=endpoint,
        encrypt_params=g.mastodon_pub_duct,
        mention_events=True,
    )

    current_app.logger.debug("Subscribed.")
    current_app.logger.debug(response)
    return response


@click.command("mastodon-test")
def mastodon_test_command():
    """
    Toot a test message and check push subscription.
    """
    click.echo("mastodon_test_command() called.")
    m = get_mastodon()

    m.toot("test")
    click.echo("tooted test message")
    click.echo("mastodon_test_command() done.")


@click.command("mastodon-subscribe")
def mastodon_subscribe_command():
    """
    Subscribe to Mastodon mention push notifications.
    """
    m = get_mastodon()
    sub = None

    # Check if there's a subscription already
    try:
        sub = m.push_subscription()
        click.echo(f"Got an existing subscription: {sub}")
    except MastodonNotFoundError as e:
        click.echo(e)

        # Add subscription
        sub = subscribe()

    sub_id = sub["id"]
    sub_key = sub["server_key"]
    click.echo(f"Push subscription ID: {sub_id}. Key: {sub_key}")

    click.echo("mastodon_subscribe_command() done.")


@click.command("mastodon-unsubscribe")
def mastodon_unsubscribe_command():
    """
    Delete push subscription.
    """
    m = get_mastodon()
    m.push_subscription_delete()
    click.echo("Deleted push subscription.")


def init_app(app):
    # https://flask.palletsprojects.com/en/2.2.x/tutorial/database/#register-with-the-application
    app.cli.add_command(mastodon_test_command)
    app.cli.add_command(mastodon_subscribe_command)
    app.cli.add_command(mastodon_unsubscribe_command)
