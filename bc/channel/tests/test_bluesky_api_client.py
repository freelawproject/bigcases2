from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from requests import HTTPError, ReadTimeout

from bc.channel.utils.connectors.bluesky_api.client import BlueskyAPI

PAGE_URL = "https://example.com/article/"
FAKE_BLOB = {"$type": "blob", "ref": {"$link": "abc"}, "size": 3}


def make_response(
    text: str = "", content: bytes = b"", error: Exception | None = None
) -> MagicMock:
    response = MagicMock()
    response.text = text
    response.content = content
    if error:
        response.raise_for_status.side_effect = error
    return response


def make_page(*metas: tuple[str, str | None]) -> str:
    tags = []
    for prop, content in metas:
        if content is None:
            tags.append(f'<meta property="{prop}">')
        else:
            tags.append(f'<meta property="{prop}" content="{content}">')
    return f"<html><head>{''.join(tags)}</head><body></body></html>"


@patch.object(BlueskyAPI, "post_media", return_value=FAKE_BLOB)
@patch("bc.channel.utils.connectors.bluesky_api.client.requests.get")
class FetchEmbedUrlCardTest(SimpleTestCase):
    def setUp(self) -> None:
        session_patcher = patch.object(BlueskyAPI, "_get_session")
        session_patcher.start()
        self.addCleanup(session_patcher.stop)
        self.api = BlueskyAPI("identifier", "password")

    def test_builds_card_from_open_graph_tags(
        self, mock_get, mock_post_media
    ) -> None:
        page = make_page(
            ("og:title", "A title"),
            ("og:description", "A description"),
            ("og:image", "/img/card.jpg"),
            ("og:image:type", "image/jpeg"),
        )
        mock_get.side_effect = [
            make_response(text=page),
            make_response(content=b"img"),
        ]

        card = self.api.fetch_embed_url_card(PAGE_URL)

        self.assertEqual(
            card,
            {
                "uri": PAGE_URL,
                "title": "A title",
                "description": "A description",
                "thumb": FAKE_BLOB,
            },
        )
        # Relative image URLs are resolved against the page URL.
        self.assertEqual(
            mock_get.call_args_list[1].args[0],
            "https://example.com/img/card.jpg",
        )
        mock_post_media.assert_called_once_with(b"img", "image/jpeg")

    def test_defaults_for_missing_optional_tags(
        self, mock_get, mock_post_media
    ) -> None:
        page = make_page(("og:image", "https://cdn.example.com/card.png"))
        mock_get.side_effect = [
            make_response(text=page),
            make_response(content=b"img"),
        ]

        card = self.api.fetch_embed_url_card(PAGE_URL)

        assert card is not None
        self.assertEqual(card["title"], "")
        self.assertEqual(card["description"], "")
        self.assertEqual(
            mock_get.call_args_list[1].args[0],
            "https://cdn.example.com/card.png",
        )
        mock_post_media.assert_called_once_with(b"img", "image/png")

    def test_no_image_tag_returns_none(
        self, mock_get, mock_post_media
    ) -> None:
        mock_get.return_value = make_response(
            text=make_page(("og:title", "A title"))
        )

        self.assertIsNone(self.api.fetch_embed_url_card(PAGE_URL))
        mock_get.assert_called_once()
        mock_post_media.assert_not_called()

    def test_image_tag_without_content_returns_none(
        self, mock_get, mock_post_media
    ) -> None:
        mock_get.return_value = make_response(
            text=make_page(("og:image", None))
        )

        self.assertIsNone(self.api.fetch_embed_url_card(PAGE_URL))
        mock_post_media.assert_not_called()

    def test_page_request_errors_return_none(
        self, mock_get, mock_post_media
    ) -> None:
        for error in (HTTPError(), ReadTimeout()):
            with self.subTest(error=error):
                mock_get.side_effect = None
                mock_get.return_value = make_response(error=error)
                self.assertIsNone(self.api.fetch_embed_url_card(PAGE_URL))
        mock_post_media.assert_not_called()

    def test_image_request_error_returns_none(
        self, mock_get, mock_post_media
    ) -> None:
        mock_get.side_effect = [
            make_response(text=make_page(("og:image", "/card.png"))),
            make_response(error=HTTPError()),
        ]

        self.assertIsNone(self.api.fetch_embed_url_card(PAGE_URL))
        mock_post_media.assert_not_called()

    def test_failed_upload_returns_none(
        self, mock_get, mock_post_media
    ) -> None:
        mock_post_media.return_value = None
        mock_get.side_effect = [
            make_response(text=make_page(("og:image", "/card.png"))),
            make_response(content=b"img"),
        ]

        self.assertIsNone(self.api.fetch_embed_url_card(PAGE_URL))
