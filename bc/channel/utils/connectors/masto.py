import base64
import logging
import re
from textwrap import shorten

from django.conf import settings
from django.urls import reverse
from mastodon import Mastodon

from bc.core.utils.images import TextImage

from .base import ApiWrapper

masto_regex = re.compile(r"@(.+)@(.+)")
logger = logging.getLogger(__name__)


class MastodonConnector:
    def __init__(self) -> None:
        self.api = self.get_api_object()

    def get_api_object(self, version=None) -> ApiWrapper:
        mastodon = Mastodon(
            api_base_url=settings.MASTODON_SERVER,
            access_token=settings.MASTODON_TOKEN,
        )

        logger.debug(f"Created Mastodon instance: {mastodon}")

        return mastodon

    def upload_media(self, media, alt_text) -> int:
        media_dict = self.api.media_post(
            media,
            mime_type="image/png",
            focus=(0, 1),
            description=shorten(
                alt_text,
                width=1500,
                placeholder="…",
            ),
        )
        return media_dict["id"]

    def add_status(
        self,
        message: str,
        text_image: TextImage | None = None,
        thumbnails=None,
    ) -> int:
        media_ids = None
        if text_image:
            media_id = self.upload_media(
                text_image.to_bytes(),
                f"An image of the entry's full text: {text_image.description}",
            )
            media_ids = [media_id]

        if thumbnails:
            for idx, thumbnail in enumerate(thumbnails):
                media_id = self.upload_media(
                    thumbnail, f"Thumbnail of page {idx + 1}"
                )
                if media_ids:
                    media_ids.append(media_id)
                else:
                    media_ids = [media_id]

        api_response = self.api.status_post(message, media_ids=media_ids)

        return api_response["id"]

    def get_keys(self):
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

    def subscribe(self, force=False):
        _, pub_dict = self.get_keys()

        endpoint = reverse("mastodon_push_handler")
        response = self.api.push_subscription_set(
            endpoint=endpoint,
            encrypt_params=pub_dict,
            mention_events=True,
        )

        return response
