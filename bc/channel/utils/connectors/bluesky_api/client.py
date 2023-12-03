import re
from datetime import datetime, timezone

import requests

from .types import (
    ImageBlob,
    Record,
    RegexMatch,
    Session,
    TextAnnotation,
    Thumbnail,
)

_BASE_API_URL = "https://bsky.social/xrpc"
_DEFAULT_CONTENT_TYPE = "application/json"
DEFAULT_LANGUAGE_CODE1 = "en"


class BlueskyAPI:
    def __init__(
        self, identifier: str, password: str, timeout: int = 30
    ) -> None:
        self._identifier = identifier
        self._password = password
        self._timeout = timeout
        self._session = self._get_session()

    def _get_session(self) -> Session:
        """
        Create an authentication session

        Returns:
            Session: response with the "accessJwt", "refreshJwt", "handle" and "did"
        """
        response = requests.post(
            f"{_BASE_API_URL}/com.atproto.server.createSession",
            headers={
                "Content-Type": _DEFAULT_CONTENT_TYPE,
            },
            json={
                "identifier": self._identifier,
                "password": self._password,
            },
            timeout=self._timeout,
        )
        return Session(**response.json())

    def post_media(self, media: bytes, mime_type: str) -> ImageBlob:
        """
        Upload bytes data (a "blob") using the given content type.

        Args:
            media (bytes): The file to be attached.
            mime_type (str): The MIME type of the content being uploaded.

        Returns:
            ImageBlob: response with the size, $type, $ref of the file.
        """
        # this size limit is specified in the app.bsky.embed.images lexicon
        if len(media) > 1000000:
            raise Exception(
                f"image file size too large. 1000000 bytes maximum, got: {len(media)}"
            )

        resp = requests.post(
            f"{_BASE_API_URL}/com.atproto.repo.uploadBlob",
            headers={
                "Content-Type": mime_type,
                "Authorization": f"Bearer {self._session.accessJwt}",
            },
            data=media,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        blob = resp.json()["blob"]
        return blob

    def get_current_time_iso(self) -> str:
        """Get current time in Server Timezone (UTC) and ISO format."""
        return datetime.now(timezone.utc).isoformat()

    def _parse_urls(self, text: str) -> list[RegexMatch]:
        """
        Parses a URL from text.

        This helper function takes a string as input and attempts to extract
        URLs from it. If any URLs are found, they are appended to a list of
        URLs. If no URLs are found, an empty list is returned.

        Args:
            text (str): The text to parse.

        Returns:
            list[RegexMatch]: List of matches.
        """
        spans = []
        # partial/naive URL regex based on: https://stackoverflow.com/a/3809435
        # tweaked to disallow some training punctuation
        url_regex = rb"[$|\W](https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*[-a-zA-Z0-9@%_\+~#//=])?)"
        text_bytes = text.encode("UTF-8")
        for m in re.finditer(url_regex, text_bytes):
            spans.append(
                RegexMatch(
                    start=m.start(1),
                    end=m.end(1),
                    text=m.group(1).decode("UTF-8"),
                )
            )
        return spans

    def _parse_text_facets(self, text) -> list[TextAnnotation]:
        """
        Parses text and extracts text annotations (e.g., links and mentions)

        This method takes a text string as input and identifies various facets,
        such as named entities (mentions) and links. It returns a list of text
        annotations, where each annotation represents a specific facet identified
        in the text. Each annotation includes the starting and ending byte
        positions of the facet within the text, along with its type.

        Args:
            text (str): The text string to parse.

        Returns:
            List[TextAnnotation]: A list of text annotations. Each annotation
            includes the starting and ending byte positions of the facet within
            the text, along with its type.
        """
        facets = []
        annotation: TextAnnotation
        for u in self._parse_urls(text):
            annotation = {
                "index": {
                    "byteStart": u.start,
                    "byteEnd": u.end,
                },
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#link",
                        "uri": u.text,
                    }
                ],
            }
            facets.append(annotation)
        return facets

    def post_status(self, text: str, media: list[Thumbnail]) -> dict[str, str]:
        """
        Creates a new status post on Bluesky using the provided text and thumbnails.

        Args:
            text: The text content of the status post.
            media: A list of dicts representing the thumbnails for the new post.

        Returns:
            dict[str, str]: Response including the cid and the uri of the record.
        """
        # Fetch the current time
        now = self.get_current_time_iso()
        message_object: Record = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "facets": self._parse_text_facets(text),
            "createdAt": now,
        }

        if media:
            message_object["embed"] = {
                "$type": "app.bsky.embed.images",
                "images": media,
            }

        response = requests.post(
            f"{_BASE_API_URL}/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {self._session.accessJwt}"},
            json={
                "repo": self._session.did,
                "collection": "app.bsky.feed.post",
                "record": message_object,
            },
            timeout=self._timeout,
        )

        return response.json()
