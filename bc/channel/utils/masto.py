import base64
import logging
import re

from django.conf import settings
from mastodon import Mastodon
from django.urls import reverse

masto_regex = re.compile(r"@(.+)@(.+)")
logger = logging.getLogger(__name__)


def get_mastodon():
    mastodon = Mastodon(
        api_base_url=settings.MASTODON_SERVER,
        access_token=settings.MASTODON_TOKEN,
    )
    logger.debug(f"Created Mastodon instance: {mastodon}")
    return mastodon


def get_keys():
    if (
        settings.MASTODON_SHARED_KEY
        and settings.MASTODON_PUBLIC_KEY
        and settings.MASTODON_PRIVATE_KEY
    ):
        shared_key = base64.b64decode(settings.MASTODON_SHARED_KEY)
        priv_dict = {
            "auth": shared_key,
            "privkey": settings.MASTODON_PRIVATE_KEY,
        }
        pub_dict = {
            "auth": shared_key,
            "pubkey": base64.b64decode(settings.MASTODON_PUBLIC_KEY),
        }
        return priv_dict, pub_dict
    else:
        raise Exception("Mastodon key are not provided")


def subscribe(force=False):
    m = get_mastodon()
    priv_dict, pub_dict = get_keys()

    endpoint = reverse('mastodon_push_handler')
    response = m.push_subscription_set(
        endpoint=endpoint,
        encrypt_params=pub_dict,
        mention_events=True,
    )

    return response
