import logging

from bc.core.utils.images import TextImage

from .alt_text_utils import text_image_alt_text, thumb_num_alt_text
from .threads_api.client import ThreadsAPI

logger = logging.getLogger(__name__)


class ThreadsConnector:
    def __init__(
        self, account: str, account_id: str, access_token: str
    ) -> None:
        self.account = account
        self.account_id = account_id
        self.access_token = access_token
        self.api = self.get_api_object()

    def get_api_object(self, _version=None) -> ThreadsAPI:
        """
        Returns an instance of the ThreadsAPI class.
        """
        api = ThreadsAPI(
            self.account_id,
            self.access_token,
        )
        return api

    def upload_media(self, media: bytes, _alt_text=None) -> str:
        return self.api.resize_and_upload_to_public_storage(media)

    def add_status(
        self,
        message: str,
        text_image: TextImage | None = None,
        thumbnails: list[bytes] | None = None,
    ) -> int:
        """
        Creates a new status update using the Threads API.
        """
        media: list[str] = []

        # Count media elements to determine type of post:
        multiple_thumbnails = thumbnails is not None and len(thumbnails) > 1
        text_image_and_thumbnail = (
            thumbnails is not None
            and len(thumbnails) > 0
            and text_image is not None
        )
        is_carousel_item = multiple_thumbnails or text_image_and_thumbnail

        if text_image:
            image_url = self.upload_media(text_image.to_bytes())
            item_container_id = self.api.create_image_container(
                image_url,
                message,
                text_image_alt_text(text_image.description),
                is_carousel_item,
            )
            if item_container_id:
                media.append(item_container_id)

        if thumbnails:
            for idx, thumbnail in enumerate(thumbnails):
                thumbnail_url = self.upload_media(thumbnail)
                item_container_id = self.api.create_image_container(
                    thumbnail_url,
                    message,
                    thumb_num_alt_text(idx),
                    is_carousel_item,
                )
                if not item_container_id:
                    continue
                media.append(item_container_id)

        # Carousel post (multiple images)
        if len(media) > 1:
            container_id = self.api.create_carousel_container(media, message)
        # Single image post
        elif len(media) == 1:
            container_id = media[0]
        # Text-only post
        else:
            container_id = self.api.create_text_only_container(message)

        return self.api.publish_container(container_id)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__module__}.{self.__class__.__name__}: "
            f"account:'{self.account}'>"
        )
