from django.conf import settings
from TwitterAPI import TwitterAPI

from bc.core.utils.images import TextImage

from .base import ApiWrapper


class TwitterConnector:
    def __init__(self) -> None:
        self.api = self.get_api_object("1.1")
        self.api_v2 = self.get_api_object("2")

    def get_api_object(self, version=None) -> ApiWrapper:
        """
        Returns an instance of the TwitterAPI class.
        """
        api = TwitterAPI(
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET,
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET,
            api_version=version,
        )
        return api

    def add_status(self, message: str, text_image: TextImage | None) -> int:
        """
        Creates a new status update using the Twitter API.

        The current implementation of the Twitter API(version 2) doesn't have an endpoint
        to upload media files, but We can upload the files using the v1.1 media endpoint
        and then We can attach previously uploaded media to a Tweet using the v2 API Tweet
        endpoint.
        """
        if text_image:
            media_response = self.api.request(
                "media/upload", None, {"media": text_image.to_bytes()}
            )
            media_id = media_response.json()["media_id"]
            response = self.api_v2.request(
                "tweets",
                params={
                    "text": message,
                    "media": {"media_ids": [str(media_id)]},
                },
                method_override="POST",
            )
            data = response.json()
        else:
            response = self.api_v2.request(
                "tweets", params={"text": message}, method_override="POST"
            )
            response.response.raise_for_status()
            data = response.json()

        return data["data"]["id"]
