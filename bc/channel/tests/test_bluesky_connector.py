from unittest.mock import call, patch

from django.test import SimpleTestCase

from bc.channel.tests.factories import fake_token
from bc.channel.utils.connectors.alt_text_utils import thumb_num_alt_text
from bc.channel.utils.connectors.bluesky import BlueskyConnector
from bc.core.utils.tests.base import faker


class ReprTest(SimpleTestCase):
    @patch("bc.channel.utils.connectors.bluesky_api.client.BlueskyAPI")
    @patch.object(BlueskyConnector, "get_api_object")
    def test_repr(self, _get_api_object, _mock_bluesky_api):
        identifier = "bigcases.bots.law"
        bluesky_conn = BlueskyConnector(identifier, fake_token())
        self.assertEqual(
            repr(bluesky_conn),
            f"<bc.channel.utils.connectors.bluesky.BlueskyConnector: identifier:'{identifier}'>",
        )


class UploadMediaTest(SimpleTestCase):
    @patch("bc.core.utils.images.TextImage")
    @patch("bc.channel.utils.connectors.bluesky_api.client.BlueskyAPI")
    @patch.object(BlueskyConnector, "get_api_object")
    def test_api_req_media_upload(
        self, get_api_object, mock_bluesky_api, mock_image
    ):
        get_api_object.return_value = mock_bluesky_api

        bluesky_conn = BlueskyConnector(fake_token(), fake_token())
        bluesky_conn.upload_media(mock_image, "image alt text")

        expected_upload_media_calls = [
            call(
                mock_image,
                mime_type="image/png",
            ),
        ]
        mock_bluesky_api.post_media.assert_has_calls(
            expected_upload_media_calls, any_order=True
        )


class AddStatusTest(SimpleTestCase):
    @patch.object(BlueskyConnector, "get_api_object")
    def test_no_image_no_thumbs(self, mock_get_api):
        mock_get_api().status_post.return_value = {"cid": "1"}

        bluesky_conn = BlueskyConnector(fake_token(), fake_token())
        result = bluesky_conn.add_status("this is the message")

        self.assertEqual(result, "1")
        bluesky_conn.api.status_post.assert_called_with(
            "this is the message",
            [],
        )

    @patch.object(BlueskyConnector, "upload_media", side_effect=[42])
    @patch("bc.core.utils.images.TextImage")
    @patch("bc.channel.utils.connectors.bluesky_api.client.BlueskyAPI")
    @patch.object(BlueskyConnector, "get_api_object")
    def test_has_image(
        self, bluesky_conn, mock_bluesky_api, mock_image, _mock_upload_media
    ):
        bluesky_conn.get_api_object.return_value = mock_bluesky_api
        mock_image.description = "test alt text"

        bluesky_conn = BlueskyConnector(fake_token(), fake_token())
        bluesky_conn.add_status("this has an image", text_image=mock_image)

        bluesky_conn.api.status_post.assert_called_with(
            "this has an image",
            [{"alt": "The entry's text: test alt text", "image": 42}],
        )

    @patch.object(BlueskyConnector, "upload_media")
    @patch("bc.core.utils.images.TextImage")
    @patch("bc.channel.utils.connectors.bluesky_api.client.BlueskyAPI")
    @patch.object(BlueskyConnector, "get_api_object")
    def test_imageupload(
        self, bluesky_conn, mock_bluesky_api, mock_image, mock_upload_media
    ):
        bluesky_conn.get_api_object.return_value = mock_bluesky_api
        mock_image.description = "the image description"
        mock_image.to_bytes.return_value = "image bytes"

        bluesky_conn = BlueskyConnector(fake_token(), fake_token())
        bluesky_conn.add_status(
            "this has an image",
            text_image=mock_image,
        )
        mock_upload_media.assert_called_with(
            "image bytes",
            None,
        )

    @patch.object(BlueskyConnector, "upload_media", side_effect=[2, 3, 5, 8])
    @patch("bc.channel.utils.connectors.bluesky_api.client.BlueskyAPI")
    @patch.object(BlueskyConnector, "get_api_object")
    def test_has_thumbnails(
        self, bluesky_conn, mock_bluesky_api, _mock_upload_media
    ):
        thumbnail_ids = [2, 3, 5, 8]

        thumbnails = [faker.binary(x) for x in thumbnail_ids]
        thumbnail_alt_texts = [
            thumb_num_alt_text(x) for x in range(len(thumbnails))
        ]
        thumbnail_dicts = [
            {"alt": alt, "image": image_id}
            for alt, image_id in zip(thumbnail_alt_texts, thumbnail_ids)
        ]
        bluesky_conn.get_api_object.return_value = mock_bluesky_api

        bluesky_conn = BlueskyConnector(fake_token(), fake_token())
        bluesky_conn.add_status(
            "this has 4 thumbnails",
            thumbnails=thumbnails,
        )

        bluesky_conn.api.status_post.assert_called_with(
            "this has 4 thumbnails",
            thumbnail_dicts,
        )

    @patch.object(BlueskyConnector, "upload_media")
    @patch("bc.channel.utils.connectors.bluesky_api.client.BlueskyAPI")
    @patch.object(BlueskyConnector, "get_api_object")
    def test_thumbnails_upload(
        self, bluesky_conn, mock_bluesky_api, mock_upload_media
    ):
        bluesky_conn.get_api_object.return_value = mock_bluesky_api
        thumb_1 = faker.binary(2)
        thumb_2 = faker.binary(3)
        expected_upload_media_calls = [
            call(thumb_1, None),
            call(thumb_2, None),
        ]

        bluesky_conn = BlueskyConnector(fake_token(), fake_token())
        bluesky_conn.add_status(
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
