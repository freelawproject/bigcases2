from unittest.mock import call, patch

from django.test import SimpleTestCase

from bc.channel.tests.factories import fake_token
from bc.channel.utils.connectors.masto import (
    MastodonConnector,
    get_handle_parts,
)
from bc.core.utils.tests.base import faker


class GetServerUrlTest(SimpleTestCase):
    def test_can_get_handle_parts(self):
        test_inputs = [
            {
                "handle": "@username@mastodon.social",
                "server_url": "https://mastodon.social/",
                "username": "username",
            },
            {
                "handle": "@bigcases@law.builders",
                "server_url": "https://law.builders/",
                "username": "bigcases",
            },
            {
                "handle": "@bottest@mastodon.nl",
                "server_url": "https://mastodon.nl/",
                "username": "bottest",
            },
        ]

        for test in test_inputs:
            # Using a subTest to guarantee each case runs even if one fails
            with self.subTest(test=test):
                account_part, instance_part = get_handle_parts(test["handle"])
                self.assertEqual(instance_part, test["server_url"])
                self.assertEqual(account_part, test["username"])


class UploadMediaTest(SimpleTestCase):
    @patch("bc.core.utils.images.TextImage")
    @patch("mastodon.Mastodon")
    @patch.object(MastodonConnector, "get_api_object")
    def test_api_req_media_upload(
        self, mock_mastodon_get_api, mock_mastodon_api, mock_image
    ):
        mock_mastodon_get_api.get_api_object.return_value = mock_mastodon_api

        mastodon_conn = MastodonConnector(
            fake_token(), fake_token(), fake_token()
        )
        mastodon_conn.upload_media(mock_image, "image alt text")

        mastodon_conn.api.media_post.assert_called_with(
            mock_image,
            mime_type="image/png",
            focus=(0, 1),
            description="image alt text",
        )


class AddStatusTest(SimpleTestCase):
    @patch.object(MastodonConnector, "get_api_object")
    def test_no_image_no_thumbs(self, mock_get_api):
        mock_get_api().status_post.return_value = {"id": "1"}

        mastodon_conn = MastodonConnector(
            fake_token(), fake_token(), fake_token()
        )
        result = mastodon_conn.add_status("this is the message")

        self.assertEqual(result, "1")
        mastodon_conn.api.status_post.assert_called_with(
            "this is the message",
            media_ids=[],
        )

    @patch.object(MastodonConnector, "upload_media", side_effect=[42])
    @patch("bc.core.utils.images.TextImage")
    @patch("mastodon.Mastodon")
    @patch.object(MastodonConnector, "get_api_object")
    def test_has_image(
        self, mastodon_conn, mock_mastodon_api, mock_image, _mock_upload_media
    ):
        mastodon_conn.get_api_object.return_value = mock_mastodon_api

        mastodon_conn = MastodonConnector(
            fake_token(), fake_token(), fake_token()
        )
        mastodon_conn.add_status("this has an image", text_image=mock_image)

        mastodon_conn.api.status_post.assert_called_with(
            "this has an image",
            media_ids=[42],
        )

    @patch.object(MastodonConnector, "upload_media")
    @patch("bc.core.utils.images.TextImage")
    @patch("mastodon.Mastodon")
    @patch.object(MastodonConnector, "get_api_object")
    def test_image_alt_text(
        self, mastodon_conn, mock_mastodon_api, mock_image, mock_upload_media
    ):
        mastodon_conn.get_api_object.return_value = mock_mastodon_api
        mock_image.description = "the image description"
        mock_image.to_bytes.return_value = "image bytes"

        mastodon_conn = MastodonConnector(
            fake_token(), fake_token(), fake_token()
        )
        mastodon_conn.add_status(
            "this has an image",
            text_image=mock_image,
        )
        mock_upload_media.assert_called_with(
            "image bytes",
            "The entry's text: the image description",
        )

    @patch.object(MastodonConnector, "upload_media", side_effect=[2, 3, 5, 8])
    @patch("mastodon.Mastodon")
    @patch.object(MastodonConnector, "get_api_object")
    def test_has_thumbnails(
        self, mastodon_conn, mock_mastodon_api, _mock_upload_media
    ):
        thumb_1 = faker.binary(2)
        thumb_2 = faker.binary(3)
        thumb_3 = faker.binary(5)
        thumb_4 = faker.binary(8)
        mastodon_conn.get_api_object.return_value = mock_mastodon_api

        mastodon_conn = MastodonConnector(
            fake_token(), fake_token(), fake_token()
        )
        mastodon_conn.add_status(
            "this has 4 thumbnails",
            thumbnails=[thumb_1, thumb_2, thumb_3, thumb_4],
        )

        mastodon_conn.api.status_post.assert_called_with(
            "this has 4 thumbnails",
            media_ids=[2, 3, 5, 8],
        )

    @patch.object(MastodonConnector, "upload_media")
    @patch("mastodon.Mastodon")
    @patch.object(MastodonConnector, "get_api_object")
    def test_thumbnails_alt_text(
        self, mastodon_conn, mock_mastodon_api, mock_upload_media
    ):
        mastodon_conn.get_api_object.return_value = mock_mastodon_api
        thumb_1 = faker.binary(2)
        thumb_2 = faker.binary(3)
        expected_upload_media_calls = [
            call(thumb_1, "Thumbnail of page 1 of the PDF linked above."),
            call(thumb_2, "Thumbnail of page 2 of the PDF linked above."),
        ]

        mastodon_conn = MastodonConnector(
            fake_token(), fake_token(), fake_token()
        )
        mastodon_conn.add_status(
            "this has 2 thumbnails",
            None,
            thumbnails=[
                thumb_1,
                thumb_2,
            ],
        )
        mock_upload_media.assert_has_calls(
            expected_upload_media_calls, any_order=True
        )


class ReprTest(SimpleTestCase):
    @patch("mastodon.Mastodon")
    @patch.object(MastodonConnector, "get_api_object")
    def test_repr(self, _get_api_object, _mock_mastodon_api):
        handle = "@bigcases@law.builders"
        account_part, instance_part = get_handle_parts(handle)
        mastodon_conn = MastodonConnector(
            fake_token(), instance_part, account_part
        )
        self.assertEqual(
            repr(mastodon_conn),
            f"<bc.channel.utils.connectors.masto.MastodonConnector: base_url:'{instance_part}', account:'{account_part}'>",
        )
