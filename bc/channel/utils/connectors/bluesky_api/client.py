import logging
import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import HTTPError

from .types import (
    ImageBlob,
    Record,
    RegexMatch,
    Session,
    SocialCard,
    TextAnnotation,
    Thumbnail,
)

logger = logging.getLogger(__name__)

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

    def post_media(self, media: bytes, mime_type: str) -> ImageBlob | None:
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
            logger.error(
                f"image file size too large. 1000000 bytes maximum, got: {len(media)}"
            )
            return None

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

    def _parse_tags(self, text: str) -> list[RegexMatch]:
        """
        Parses hashtags from text.

        This helper function takes a string as input and attempts to extract
        hashtags from it. If any hashtags are found, they are appended to a
        list of hashtags. If no hashtags are found, an empty list is returned.

        Args:
            text (str): The text to parse.

        Returns:
            list[RegexMatch]: List of matches.
        """
        spans = []
        # reference: https://github.com/bluesky-social/atproto/blob/fbc7e75c402e0c268e7e411353968985eeb4bb06/packages/api/src/rich-text/util.ts#L10
        # given that our needs of a hashtag is very simple, we can do away with
        # only parsing alphanumeric characters
        tag_regex = rb"(?:^|\s)#(?P<tag>[0-9]*[a-zA-Z][a-zA-Z0-9]*)"
        text_bytes = text.encode("UTF-8")
        for m in re.finditer(tag_regex, text_bytes):
            spans.append(
                RegexMatch(
                    start=m.start("tag") - 1,
                    end=m.end("tag"),
                    text=m.group("tag").decode("UTF-8"),
                )
            )
        return spans

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

    def _parse_embedded_links(self, text: str) -> list[RegexMatch]:
        """
        Parses embedded links from text.

        This helper method attempts to identify and return all occurrences of
        link markup in the provided text. If no occurrences are found, an empty
        list is returned.

        Args:
            text (str): The text to parse.

        Returns:
            list[RegexMatch]: List of matches.
        """
        spans = []
        # Matches anything that isn't a square closing bracket
        name_regex = "[^]]+"
        # Matches http:// or https:// followed by anything but a closing parenthesis
        url_regex = "http[s]?://[^)]+"
        # Combined regex expression with named groups.
        markup_regex = (
            rf"(?P<name>\[{name_regex}])(?P<uri>\(\s*{url_regex}\s*\))"
        ).encode()
        text_bytes = text.encode("UTF-8")
        offset = 0
        for m in re.finditer(markup_regex, text_bytes):
            # Remove parenthesis and whitespaces from the uri
            cleaned_uri = re.sub(
                r"\(\s*|\s*\)", "", m.group("uri").decode("UTF-8")
            )
            # We need the offset variable to fine-tune the target word's
            # position and ensure the link is created in the right spot
            # because We run the regex on the full text with links, but
            # only post the cleaned-up version without them
            spans.append(
                RegexMatch(
                    start=m.start("name") - offset,
                    end=m.end("name") - offset,
                    text=cleaned_uri,
                )
            )
            offset += len(m.group("uri"))
        return spans

    def _clean_text(sef, text: str) -> str:
        """
        Removes all link markup notations from a given text, leaving only the
        plain text content.

        This helper function specifically targets the markup used for embedding
        hyperlinks within the provided text. It aims to strip away all URLs
        associated with links, leaving behind the raw textual information.

        Args:
            text (str): the text to be cleansed of link markup.

        Returns:
            str: string containing the original text with all link markup
            notations removed.
        """
        return re.sub(r"(?<=])\(\S+\)", "", text)

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
        for u in self._parse_embedded_links(text):
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

        text = self._clean_text(text)
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

        for u in self._parse_tags(text):
            annotation = {
                "index": {
                    "byteStart": u.start,
                    "byteEnd": u.end,
                },
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#tag",
                        "tag": u.text,
                    }
                ],
            }
            facets.append(annotation)
        return facets

    def fetch_embed_url_card(self, url: str) -> SocialCard | None:
        """
        Fetches metadata from a given URL to add the rendered preview in a post

        This method uses the Open Graph protocol to extract metadata from the
        provided url and build a rich social card for a Bluesky post.

        Args:
            url (str): The URL to fetch the social card information from.

        Returns:
            SocialCard (optional): A dictionary containing the keys for building
            the Bluesky post social card
        """
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": "bots.law"},
                timeout=self._timeout,
            )
            resp.raise_for_status()
        except HTTPError:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # parse out the "og:title" and "og:description" HTML meta tags
        title_tag = soup.find("meta", property="og:title")
        description_tag = soup.find("meta", property="og:description")

        # if there is an "og:image" HTML meta tag, fetch and upload that image
        image_tag = soup.find("meta", property="og:image")
        if not image_tag:
            return None

        mime_tag = soup.find("meta", property="og:image:type")
        mime_type = mime_tag["content"] if mime_tag else "image/png"
        img_url = urljoin(url, image_tag["content"])
        try:
            resp = requests.get(img_url, timeout=self._timeout)
            resp.raise_for_status()
        except HTTPError:
            return None

        thumbnail = self.post_media(resp.content, mime_type)
        if not thumbnail:
            return None

        return {
            "uri": url,
            "title": title_tag["content"] if title_tag else "",
            "description": (
                description_tag["content"] if description_tag else ""
            ),
            "thumb": thumbnail,
        }

    def post_status(self, text: str, media: list[Thumbnail]) -> dict[str, str]:
        """
        Creates a new status post on Bluesky using the provided text and thumbnails.

        Args:
            text: The text content of the status post.
            media: A list of dicts representing the thumbnails for the new post.

        Returns:
            dict[str, str]: Response including the cid and the uri of the record.
        """
        now = self.get_current_time_iso()
        message_object: Record = {
            "$type": "app.bsky.feed.post",
            "text": self._clean_text(text),
            "facets": self._parse_text_facets(text),
            "createdAt": now,
        }

        if media:
            message_object["embed"] = {
                "$type": "app.bsky.embed.images",
                "images": media,
            }
        elif message_object["facets"]:
            link: str | None = None
            card: SocialCard | None = None

            for facet in message_object["facets"]:
                feature = facet["features"][0]
                if feature["$type"] == "app.bsky.richtext.facet#link":
                    link = feature["uri"]

            if link:
                card = self.fetch_embed_url_card(link)

            if card:
                message_object["embed"] = {
                    "$type": "app.bsky.embed.external",
                    "external": card,
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
