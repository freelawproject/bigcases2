import logging
import time
import uuid

import requests
from django.conf import settings

from bc.core.utils.images import convert_to_jpeg, resize_image
from bc.core.utils.s3 import put_object_in_bucket

logger = logging.getLogger(__name__)


_BASE_API_URL = "https://graph.threads.net/v1.0"


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

    def publish_container(self, container_id: str) -> str | None:
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
        return response.json().get("id") if response is not None else None

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
                f"Post request to Threads API timed out\n"
                f"Request URL: {url}"
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
            settings.THREADS_BUCKET_NAME,
            settings.THREADS_BUCKET_REGION,
        )
        return image_s3_url
