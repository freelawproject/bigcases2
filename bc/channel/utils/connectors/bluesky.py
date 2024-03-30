from bc.core.utils.images import TextImage

from .alt_text_utils import text_image_alt_text, thumb_num_alt_text
from .base import ApiWrapper
from .bluesky_api.client import BlueskyAPI
from .bluesky_api.types import ImageBlob, Thumbnail


class BlueskyConnector:
    def __init__(self, identifier: str, password: str) -> None:
        self.identifier = identifier
        self.password = password
        self.api = self.get_api_object()

    def get_api_object(self, _version=None) -> ApiWrapper:
        return BlueskyAPI(self.identifier, self.password)

    def upload_media(self, media, alt_text) -> ImageBlob:
        """Upload a new blob to be added to a post in a later request."""
        return self.api.post_media(media, mime_type="image/png")

    def add_status(
        self,
        message: str,
        text_image: TextImage | None = None,
        thumbnails: list[bytes] | None = None,
    ) -> str:
        """Send post with attached image."""
        media: list[Thumbnail] = []
        if text_image:
            blob = self.upload_media(text_image.to_bytes(), None)
            if blob:
                media.append(
                    {
                        "alt": text_image_alt_text(text_image.description),
                        "image": blob,
                    }
                )

        if thumbnails:
            for idx, thumbnail in enumerate(thumbnails):
                blob = self.upload_media(thumbnail, None)
                if not blob:
                    continue
                media.append(
                    {
                        "alt": thumb_num_alt_text(idx),
                        "image": blob,
                    }
                )

        api_response = self.api.post_status(message, media)

        return api_response["cid"]
