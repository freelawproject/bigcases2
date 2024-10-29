import logging
import requests

logger = logging.getLogger(__name__)


_BASE_API_URL = "https://graph.threads.net/v1.0/"

class ThreadsAPI:
    def __init__(
        self, account_id: str, access_token: str
    ) -> None:
        self._account_id = account_id
        self._access_token = access_token
        self._base_account_url = f"{_BASE_API_URL}/{self._account_id}"

    def upload_media(
        self,
        media: bytes,
        message: str,
        alt_text: str,
        is_carousel_item: bool = False,
    ) -> str:
        print("to do: upload media to S3 and get URL")
        image_url = f"https://www.example.com/{media.hex()}.png"
        container_id = self._create_item_container(
            image_url,
            message,
            alt_text,
            is_carousel_item,
        )
        return container_id

    def publish_container(self, container_id: str) -> int:
        base_url = f"{self._base_account_url}/threads_publish"
        params = {
            "creation_id": container_id,
            "access_token": self._access_token,
        }
        response = requests.post(base_url, params=params)
        return response.json()["id"]

    def _create_item_container(
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
        response = requests.post(base_url, params=params)
        return response.json()["id"]

    def create_carousel_container(
        self, children: list[str], text: str,
    ):
        base_url = f"{self._base_account_url}/threads"
        params = {
            "access_token": self._access_token,
            "media_type": "IMAGE",
            "children": children,
        }
        response = requests.post(base_url, params=params)
        return response.json()["id"]
