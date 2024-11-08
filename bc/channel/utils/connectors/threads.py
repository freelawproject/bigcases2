import logging

from bc.core.utils.images import TextImage

from .alt_text_utils import text_image_alt_text, thumb_num_alt_text
from .threads_api.client import ThreadsAPI

logger = logging.getLogger(__name__)


class ThreadsConnector:
    """
    A connector for interfacing with the Threads API, which complies with
    the RefreshableBaseAPIConnector protocol.
    """

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

    def validate_access_token(self) -> tuple[bool, str]:
        """
        Ensures that the access token used by the connector is up-to-date.

        This method delegates the validation of the access token to the underlying
        `ThreadsAPI` instance by checking the access token's expiration date and
        refreshing it if necessary.

        Returns:
            tuple[bool, str]: A tuple where the first element is a boolean
             indicating whether the token was refreshed, and the second element is the current access token.
        """
        return self.api.validate_access_token()

    def upload_media(self, media: bytes, _alt_text=None) -> str:
        """
        Uploads media to public storage for Threads API compatibility.

        Since Threads API requires media to be accessible via public URL,
        this method resizes the image as needed, uploads it to S3, and
        returns the public URL.

        Args:
            media (bytes): The image bytes to be uploaded.
            _alt_text (str, optional): Alternative text for accessibility
                (not currently used, required by protocol).

        Returns:
            str: Public URL of the uploaded image.
        """
        return self.api.resize_and_upload_to_public_storage(media)

    def add_status(
        self,
        message: str,
        text_image: TextImage | None = None,
        thumbnails: list[bytes] | None = None,
    ) -> str:
        """
        Creates and publishes a new status update on Threads.

        This method determines the type of post (text-only, single image,
        or carousel) based on the provided media. If multiple images are
        provided, a carousel post is created. Otherwise, it creates a
        single image or text-only post.

        Args:
            message (str): The text content of the status.
            text_image (TextImage | None): An optional main image with text.
            thumbnails (list[bytes] | None): Optional list of thumbnails for
                a carousel post.

        Returns:
            str: The ID of the published status.
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

        # Determine container id to be published based on media count:
        if len(media) > 1:
            # Carousel post (multiple images)
            container_id = self.api.create_carousel_container(media, message)
        elif len(media) == 1:
            # Single image post
            container_id = media[0]
        else:
            # Text-only post
            container_id = self.api.create_text_only_container(message)

        if container_id is None:
            logger.error(
                "ThreadsConnector could not get container to publish!"
            )
            return ""

        return self.api.publish_container(container_id)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__module__}.{self.__class__.__name__}: "
            f"account:'{self.account}'>"
        )
