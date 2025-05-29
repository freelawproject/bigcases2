import logging
import time
import uuid
from datetime import UTC, datetime, timedelta

import requests

from bc.core.utils.images import convert_to_jpeg, resize_image
from bc.core.utils.redis import make_redis_interface
from bc.core.utils.s3 import put_object_in_bucket

logger = logging.getLogger(__name__)


_BASE_API_URL = "https://graph.threads.net/v1.0"

r = make_redis_interface("CACHE")


class ThreadsAPI:
    """
    A client for interacting with the Threads API to create and publish content.

    For single-image and text-only posts, a container with all data is created,
    then the same container is published.

    For posts with multiple images, a container for each image should be created,
    then a container for the carousel with its children, and lastly the
    carousel container is published.

    Docs: https://developers.facebook.com/docs/threads/posts
    """

    def __init__(
        self,
        account_id: str,
        access_token: str,
        timeout: int = 30,
    ) -> None:
        self._account_id = account_id
        self._access_token = access_token
        self._timeout = timeout
        self._base_account_url = f"{_BASE_API_URL}/{self._account_id}"

    def publish_container(self, container_id: str) -> str:
        """
        Publishes a media container to Threads.

        Args:
            container_id (str): The ID of the container to publish.

        Returns:
            str: The ID of the published post.
        """
        base_url = f"{self._base_account_url}/threads_publish"
        params = {
            "creation_id": container_id,
            "access_token": self._access_token,
        }
        response = self.attempt_post(base_url, params)
        return response.json().get("id") if response is not None else ""

    def create_image_container(
        self,
        image_url: str,
        message: str,
        alt_text: str,
        is_carousel_item: bool = False,
    ) -> str | None:
        """
        Creates a container for an image post on Threads, to be published
        using the method publish_container.

        Args:
            image_url (str): URL of the image to post hosted on a public server.
            message (str): Text content to accompany the image.
            alt_text (str): Alt text for accessibility.
            is_carousel_item (bool, optional): Whether the image is part of a
             carousel. Defaults to False.

        Returns:
            str: The ID of the created image container.
        """
        base_url = f"{self._base_account_url}/threads"
        params = {
            "image_url": image_url,
            "access_token": self._access_token,
            "media_type": "IMAGE",
            "alt_text": alt_text,
        }
        if is_carousel_item:
            params["is_carousel_item"] = "true"
        else:
            params["text"] = message
        response = self.attempt_post(base_url, params)
        return response.json().get("id") if response is not None else None

    def create_carousel_container(
        self,
        children: list[str],
        message: str,
    ) -> str | None:
        """
        Creates a carousel container with multiple images on Threads,
        to be published using the method publish_container.

        Args:
            children (list[str]): A list of container IDs for each image in the carousel.
            message (str): Text content to accompany the carousel.

        Returns:
            str: The ID of the created carousel container.
        """
        base_url = f"{self._base_account_url}/threads"
        params = {
            "access_token": self._access_token,
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "text": message,
        }
        response = self.attempt_post(base_url, params)
        return response.json().get("id") if response is not None else None

    def create_text_only_container(self, message: str) -> str | None:
        """
        Creates a container for a text-only post on Threads,
        to be published using the method publish_container.

        Args:
            message (str): The text content for the post.

        Returns:
            str: The ID of the created text container.
        """
        base_url = f"{self._base_account_url}/threads"
        params = {
            "access_token": self._access_token,
            "media_type": "TEXT",
            "text": message,
        }
        response = self.attempt_post(base_url, params)
        return response.json().get("id") if response is not None else None

    def attempt_post(
        self,
        url: str,
        params: dict,
    ) -> requests.Response | None:
        """
        Attempts to send a POST request to a specified URL with given parameters.
        If the request is successful, the response is returned, otherwise `None` is returned.
        """
        try:
            response = requests.post(url, params=params, timeout=self._timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.error(
                f"Post request to Threads API timed out\nRequest URL: {url}"
            )
            return None
        except requests.exceptions.HTTPError as err:
            logger.error(
                f"An error occurred when trying to post to Threads API\n"
                f"Request URL: {url}\n\n"
                f"{err}"
            )
            return None
        return response

    def validate_access_token(self) -> tuple[bool, str]:
        """
        Validates the current access token and refreshes it if necessary.

        This method checks the expiration date of the access token stored in the Redis cache.
        If the expiration date is missing, expired, or will expire within two days,
        it attempts to refresh the token by calling `refresh_access_token`.

        Returns:
            tuple[bool, str]: A tuple where the first element is a boolean
             indicating whether the token was refreshed, and the second element is the current access token.
        """
        refreshed = False

        try:
            cached_expiration_date = r.get(self._get_expiration_key())
        except Exception as e:
            logger.error(
                f"Could not retrieve cached token, will attempt to refresh.\n"
                f"Redis error: {e}"
            )
            return self.refresh_access_token(), self._access_token

        if cached_expiration_date is None:
            return self.refresh_access_token(), self._access_token

        expiration_date = datetime.fromisoformat(str(cached_expiration_date))
        delta = expiration_date - datetime.now(UTC)
        will_expire_soon = delta <= timedelta(days=2)

        if will_expire_soon:
            refreshed = self.refresh_access_token()

        return refreshed, self._access_token

    def refresh_access_token(self) -> bool:
        """
        Refreshes the access token by making a request to the Threads API.

        If the refresh is successful, it updates the access token and its expiration date in the cache.

        Returns:
            bool: `True` if the access token was successfully refreshed and updated; `False` otherwise.
        """
        refresh_access_token_url = (
            "https://graph.threads.net/refresh_access_token"
        )
        params = {
            "grant_type": "th_refresh_token",
            "access_token": self._access_token,
        }
        try:
            response = requests.get(
                refresh_access_token_url,
                params=params,
                timeout=10,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            logger.error(
                f"Failed to refresh access token for Threads account {self._account_id}:\n"
                f"{err}"
            )
            return False

        data = response.json()
        new_access_token = data.get("access_token")
        expires_in = data.get("expires_in")  # In seconds

        if new_access_token is None or expires_in is None:
            logger.error(
                f"Missing 'access_token' or 'expires_in' in refresh access token response for Threads account {self._account_id}. "
                f"If the issue persists, a new access token can be retrieved manually with the script again.\n"
                f"Response data: {data}"
            )
            return False

        self._access_token = new_access_token
        self._set_token_expiration_in_cache(expires_in)

        return True

    def _set_token_expiration_in_cache(self, expires_in: int):
        """
        Stores the access token's expiration date in the Redis cache.

        Args:
            expires_in (int): The number of seconds until the access token expires.
        """
        delay = timedelta(seconds=expires_in)
        expiration_date = (datetime.now(UTC) + delay).isoformat()
        key = self._get_expiration_key()
        try:
            r.set(
                key,
                expiration_date.encode("utf-8"),
                ex=expires_in,  # ensure the cache entry expires when the token does
            )
        except Exception as e:
            logger.error(f"Could not set {key} in cache:\n{e}")

    def _get_expiration_key(self) -> str:
        """
        Returns the Redis key used for storing the access token's expiration date.
        """
        return f"threads_token_expiration_{self._account_id}"

    @staticmethod
    def resize_and_upload_to_public_storage(media: bytes) -> str:
        """
        Processes and uploads an image to S3 to meet Threads API requirements.

        Specifically, this method:
        - Converts the image to JPEG format to ensure compatibility, as
          Threads only accepts JPEG images.
        - Resizes the image to fit within specified width and aspect ratio
          constraints required by Threads.
        - Uploads the processed image to an S3 bucket with a unique filename,
          generating a public URL that can be passed to Threads API.

        Args:
            media (bytes): The original image bytes to be processed.

        Returns:
            str: The public URL of the uploaded image in S3.
        """
        jpeg_image = convert_to_jpeg(
            image=media,
            quality=85,
        )
        resized_image = resize_image(
            image=jpeg_image,
            min_width=320,
            max_width=1440,
            min_aspect_ratio=4 / 5,
            max_aspect_ratio=1.91,
        )
        timestamp = time.strftime("%H%M%S")
        prefix = f"tmp/threads/{time.strftime('%Y/%m/%d')}/"
        file_name_in_bucket = f"{prefix}{timestamp}_{uuid.uuid4().hex}.jpeg"
        image_s3_url = put_object_in_bucket(
            resized_image,
            file_name_in_bucket,
        )
        return image_s3_url
