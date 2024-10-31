import logging

import requests
from django.conf import settings

from bc.core.utils.images import convert_to_jpeg, resize_image
from bc.core.utils.s3 import put_object_in_bucket

logger = logging.getLogger(__name__)


_BASE_API_URL = "https://graph.threads.net/v1.0"


class ThreadsAPI:
    def __init__(self, account_id: str, access_token: str) -> None:
        self._account_id = account_id
        self._access_token = access_token
        self._base_account_url = f"{_BASE_API_URL}/{self._account_id}"

    def publish_container(self, container_id: str) -> int:
        base_url = f"{self._base_account_url}/threads_publish"
        params = {
            "creation_id": container_id,
            "access_token": self._access_token,
        }
        response = requests.post(base_url, params=params)
        return response.json()["id"]

    def create_image_container(
        self,
        image_url: str,
        message: str,
        alt_text: str,
        is_carousel_item: bool = False,
    ) -> str:
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
        logger.info(f"Trying to create container for {image_url}")
        response = requests.post(base_url, params=params)
        logger.info(f"Status code image container: {response.status_code}")
        logger.info(f"Request URL : {response.url}")
        logger.info(f"Item container response: {response.json()}")
        return response.json()["id"]

    def create_carousel_container(
        self,
        children: list[str],
        message: str,
    ) -> str:
        base_url = f"{self._base_account_url}/threads"
        params = {
            "access_token": self._access_token,
            "media_type": "CAROUSEL",
            "children": children,
            "text": message,
        }
        response = requests.post(base_url, params=params)
        logger.info(f"Status code carousel container: {response.status_code}")
        logger.info(f"Request URL : {response.url}")
        logger.info(f"Carousel container response: {response.json()}")
        return response.json()["id"]

    def create_text_only_container(self, message: str) -> str:
        base_url = f"{self._base_account_url}/threads"
        params = {
            "access_token": self._access_token,
            "media_type": "TEXT",
            "text": message,
        }
        response = requests.post(base_url, params=params)
        logger.info(f"Status code text container: {response.status_code}")
        logger.info(f"Request URL : {response.url}")
        logger.info(f"Text container response: {response.json()}")
        return response.json()["id"]

    @staticmethod
    def resize_and_upload_to_public_storage(
        media: bytes,
        _alt_text=None,
    ) -> str:
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
        file_name_in_bucket = f"{media.hex()[:10]}.jpeg"
        image_s3_url = put_object_in_bucket(
            resized_image,
            file_name_in_bucket,
            settings.THREADS_BUCKET_NAME,
            settings.THREADS_BUCKET_ZONE,
        )
        return image_s3_url
