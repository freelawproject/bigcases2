import base64
import logging
import re
from textwrap import shorten

from django.conf import settings
from django.urls import reverse
from mastodon import Mastodon

from bc.core.utils.images import TextImage

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
        raise Exception(
            "Mastodon key are not provided. Please check your env file and make sure you set "
            "MASTODON_SHARED_KEY, MASTODON_PUBLIC_KEY, MASTODON_PRIVATE_KEY. You can use the "
            "get_mastodon_keys.py file to get the values required for these keys"
        )


def subscribe(force=False):
    m = get_mastodon()
    _, pub_dict = get_keys()

    endpoint = reverse("mastodon_push_handler")
    response = m.push_subscription_set(
        endpoint=endpoint,
        encrypt_params=pub_dict,
        mention_events=True,
    )

    return response


def post_status(message: str, text_image: TextImage | None) -> int:
    m = get_mastodon()
    media_ids = None
    if text_image:
        media_dict = m.media_post(
            text_image.to_bytes(),
            mime_type="image/png",
            focus=(0, 1),
            description=shorten(
                f"An image of the entry's full text: {text_image.description}",
                width=1500,
                placeholder="…",
            ),
        )
        media_ids = [media_dict["id"]]

    api_response = m.status_post(message, media_ids=media_ids)

    return api_response["id"]
