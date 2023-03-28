from textwrap import shorten
from typing import IO, Any

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

    def upload_media(self, media, alt_text) -> int:
        media_response = self.api.request(
            "media/upload", None, {"media": media}
        )
        media_id = media_response.json()["media_id"]
        self.api.request(
            "media/metadata/create",
            params={
                "media_id": media_id,
                "alt_text": {
                    "text": shorten(
                        alt_text,
                        width=1000,
                        placeholder="…",
                    )
                },
            },
        )
        return media_id

    def add_status(
        self,
        message: str,
        text_image: TextImage | None = None,
        thumbnails: list[IO[bytes]] | None = None,
    ) -> int:
        """
        Creates a new status update using the Twitter API.

        The current implementation of the Twitter API(version 2) doesn't have an endpoint
        to upload media files, but We can upload the files using the v1.1 media endpoint
        and then We can attach previously uploaded media to a Tweet using the v2 API Tweet
        endpoint.

        Here's the Twitter API endpoint map:

        https://developer.twitter.com/en/docs/twitter-api/migrate/twitter-api-endpoint-map

        This table is supposed to help with the migration to the new v2 API. We can check which
        endpoints are available. They still have several items marked as [COMING SOON] and the media
        endpoints are one of them.
        """
        media_array = []
        payload: dict[str, Any] = {"text": message}
        if text_image:
            media_id = self.upload_media(
                text_image.to_bytes(),
                f"An image of the entry's full text: {text_image.description}",
            )
            media_array.append(str(media_id))
            payload["media"] = {"media_ids": media_array}

        if thumbnails:
            for idx, thumbnail in enumerate(thumbnails):
                media_id = self.upload_media(
                    thumbnail, f"Thumbnail of page {idx + 1} of the PDF"
                )
                media_array.append(str(media_id))
            payload["media"] = {"media_ids": media_array}

        response = self.api_v2.request(
            "tweets",
            params=payload,
            method_override="POST",
        )
        response.response.raise_for_status()
        data = response.json()

        return data["data"]["id"]
