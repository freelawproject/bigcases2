from bc.core.utils.images import TextImage
from .alt_text_utils import text_image_alt_text, thumb_num_alt_text

from .base import ApiWrapper
from .threads_api.client import ThreadsAPI


class ThreadsConnector:
    def __init__(
        self, account: str, account_id: str, access_token: str
    ) -> None:
        self.account = account
        self.account_id = account_id
        self.access_token = access_token
        self.api: ThreadsAPI = self.get_api_object()

    def get_api_object(self) -> ApiWrapper:
        """
        Returns an instance of the ThreadsAPI class.
        """
        api = ThreadsAPI(
            self.account_id,
            self.access_token,
        )
        return api

    def upload_media(
        self,
        media: bytes,
        message: str,
        alt_text: str,
        is_carousel_item: bool,
    ) -> str:
        container_id = self.api.upload_media(
            media,
            message,
            alt_text,
            is_carousel_item,
        )
        return container_id

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
        is_carousel_item = (len(thumbnails) > 1 or
                            (len(thumbnails) > 0 and text_image is not None))
        if text_image:
            container_id = self.upload_media(
                text_image.to_bytes(),
                message,
                text_image_alt_text(text_image.description),
                is_carousel_item,
            )
            if container_id:
                media.append(container_id)

        if thumbnails:
            for idx, thumbnail in enumerate(thumbnails):
                container_id = self.upload_media(
                    thumbnail,
                    message,
                    thumb_num_alt_text(idx),
                    is_carousel_item,
                )
                if not container_id:
                    continue
                media.append(container_id)

        if is_carousel_item:
            container_id = self.api.create_carousel_container(media, message)
        else:
            container_id = media[0]

        return self.api.publish_container(container_id)

    def __repr__(self) -> str:
        return f"<{self.__class__.__module__}.{self.__class__.__name__}: account:'{self.account}'>"
