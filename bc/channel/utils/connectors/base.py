from typing import Protocol, Union

from mastodon import Mastodon
from TwitterAPI import TwitterAPI

from bc.core.utils.images import TextImage

from .bluesky_api.client import BlueskyAPI

ApiWrapper = Union[Mastodon, TwitterAPI, BlueskyAPI]


class BaseAPIConnector(Protocol):
    def get_api_object(self, version: str | None = None) -> ApiWrapper:
        """
        Returns an instance of an API wrapper class.

        Any authentication step required to create the API instance should
        be included in this method. This method uses the version parameter
        to handle services that uses API versioning.

        Args:
            version (str, optional): version number of the API. Defaults to None.

        Returns:
            ApiWrapper: instance of the API wrapper.
        """
        ...

    def upload_media(self, media: bytes, alt_text: str) -> int:
        """
        creates a media attachment to be used with a new status.

        This method should handle extra step if needed to provide additional
        information about the uploaded file.

        Args:
            media (bytes): The file to be attached.
            alt_text (str): A plain-text description of the media, for accessibility
            purposes.

        Returns:
            int: the unique identifier of the upload.
        """
        ...

    def add_status(
        self,
        message: str,
        text_image: TextImage | None = None,
        thumbnails: list[bytes] | None = None,
    ) -> int:
        """
        Creates a new status using the API wrapper object and returns the integer
        representation of the identifier for the new status.

        This method should handle any extra step needed to attach/upload images before
        creating a status update using the API object.

        Args:
            message (str): Text to include in the new status
            text_image (TextImage | None): Image to attach to the new status
            thumbnails ( list[bytes] | None): list of thumbnail images to include

        Returns:
            int: The unique identifier for the new status.
        """
        ...
