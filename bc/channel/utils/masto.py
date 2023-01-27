import logging
import re

from django.conf import settings
from mastodon import Mastodon

masto_regex = re.compile(r"@(.+)@(.+)")
logger = logging.getLogger(__name__)


def get_mastodon():
    mastodon = Mastodon(
        api_base_url=settings.MASTODON_SERVER,
        access_token=settings.MASTODON_TOKEN,
    )
    logger.debug(f"Created Mastodon instance: {mastodon}")
    return mastodon


def subscribe(force=False):
    m = get_mastodon()
    priv_dict, pub_dict = m.push_subscription_generate_keys()

    # Send subscribe request
    self_url = "localhost:8000"
    endpoint = f"{self_url}/webhooks/mastodon"
    response = m.push_subscription_set(
        endpoint=endpoint,
        encrypt_params=pub_dict,
        mention_events=True,
    )

    logger.debug("Subscribed.")
    logger.debug(response)
    return response


def get_keys():
    pass
