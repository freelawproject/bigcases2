import base64
import logging
import re
from textwrap import shorten

from django.conf import settings
from django.urls import reverse
from mastodon import Mastodon
from mastodon.errors import (
    MastodonGatewayTimeoutError,
    MastodonNetworkError,
    MastodonServerError,
)

from bc.core.utils.images import TextImage

from .alt_text_utils import text_image_alt_text, thumb_num_alt_text
from .base import ApiWrapper

masto_regex = re.compile(r"@(.+)@(.+)")
logger = logging.getLogger(__name__)


def get_handle_parts(handle: str) -> tuple[str, str]:
    """
    extracts the server name from the Mastodon handle and returns the URL
    Args:
        handle (str): the mastodon handle
    Returns:
        tuple:
            str: Mastodon server's URL
            str: Mastodon handle
    """
    result = masto_regex.search(handle)
    if result:
        account_part, instance_part = result.groups()
        return (account_part, f"https://{instance_part}/")
    return ("", "")


class MastodonConnector:
    def __init__(self, access_token: str, base_url: str, account: str) -> None:
        self.access_token = access_token
        self.base_url = base_url
        self.account = account
        self.api = self.get_api_object()

    def get_api_object(self, _version=None) -> ApiWrapper:
        mastodon = Mastodon(
            api_base_url=self.base_url,
            access_token=self.access_token,
            request_timeout=60,
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
        thumbnails: list[bytes] | None = None,
    ) -> int:
        media_ids = []
        if text_image:
            try:
                media_id = self.upload_media(
                    text_image.to_bytes(),
                    text_image_alt_text(text_image.description),
                )
                media_ids.append(media_id)
            except (
                MastodonServerError,
                MastodonGatewayTimeoutError,
                MastodonNetworkError,
            ):
                # clean the media array
                media_ids = []

        if thumbnails:
            for idx, thumbnail in enumerate(thumbnails):
                try:
                    media_id = self.upload_media(
                        thumbnail, thumb_num_alt_text(idx)
                    )
                    media_ids.append(media_id)
                except (
                    MastodonServerError,
                    MastodonGatewayTimeoutError,
                    MastodonNetworkError,
                ):
                    # clean the media array and break the loop
                    media_ids = []
                    break

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

    def subscribe(self, _force=False):
        _, pub_dict = self.get_keys()

        endpoint = reverse("mastodon_push_handler")
        response = self.api.push_subscription_set(
            endpoint=endpoint,
            encrypt_params=pub_dict,
            mention_events=True,
        )

        return response

    def __repr__(self) -> str:
        return f"<{self.__class__.__module__}.{self.__class__.__name__}: base_url:'{self.base_url}', account:'{self.account}'>"
