from typing import Protocol, Union

from mastodon import Mastodon
from TwitterAPI import TwitterAPI

from bc.channel.utils.connectors.bluesky_api.client import BlueskyAPI
from bc.channel.utils.connectors.threads_api.client import ThreadsAPI
from bc.core.utils.images import TextImage

from .bluesky_api.types import ImageBlob

ApiWrapper = Union[Mastodon, TwitterAPI, BlueskyAPI, ThreadsAPI]  # noqa: UP007


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

    def upload_media(
        self, media: bytes, alt_text: str
    ) -> int | str | ImageBlob | None:
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
    ) -> int | str:
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


class RefreshableBaseAPIConnector(BaseAPIConnector, Protocol):
    """
    Extends BaseAPIConnector to add logic to validate access tokens.
    """

    def validate_access_token(self) -> tuple[bool, str]:
        """
        Validates the access token and refreshes it if necessary.

        Returns:
            tuple[bool, str]: A tuple where the first element is a boolean
             indicating if the token was refreshed, and the second element
             is the current access token.
        """
        ...
