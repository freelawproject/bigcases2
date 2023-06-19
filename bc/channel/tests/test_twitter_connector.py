from unittest.mock import patch, call

from django.test import SimpleTestCase

from bc.core.utils.tests.base import faker
from bc.channel.tests.factories import fake_token
from bc.channel.utils.connectors.twitter import TwitterConnector


class UploadMediaTest(SimpleTestCase):
    @patch("bc.core.utils.images.TextImage")
    @patch("TwitterAPI.TwitterAPI.TwitterAPI")
    @patch.object(TwitterConnector, "get_api_object")
    def test_api_req_media_upload(
        self, twitter_conn, mock_twitter_api, mock_image
    ):
        twitter_conn.get_api_object.return_value = mock_twitter_api

        twitter_conn = TwitterConnector(fake_token(), fake_token())
        twitter_conn.upload_media(mock_image, "image alt text")

        expected_upload_media_calls = [
            call("media/upload", None, {"media": mock_image}),
            call(
                "media/metadata/create",
                params={
                    "media_id": twitter_conn.get_api_object()
                    .request()
                    .json()["media_id"],
                    "alt_text": {"text": "image alt text"},
                },
            ),
        ]
        twitter_conn.get_api_object().request.assert_has_calls(
            expected_upload_media_calls, any_order=True
        )


class AddStatusTest(SimpleTestCase):
    @patch.object(TwitterConnector, "get_api_object")
    def test_no_image_no_thumbs(self, mock_get_api):
        mock_get_api().request().json.return_value = {"data": {"id": "1"}}

        twitter_conn = TwitterConnector(fake_token(), fake_token())
        result = twitter_conn.add_status("this is the message")
        self.assertEqual(result, "1")
        twitter_conn.api_v2.request.assert_called_with(
            "tweets",
            params={"text": "this is the message"},
            method_override="POST",
        )

    @patch.object(TwitterConnector, "upload_media", side_effect=[42])
    @patch("bc.core.utils.images.TextImage")
    @patch("TwitterAPI.TwitterAPI.TwitterAPI")
    @patch.object(TwitterConnector, "get_api_object")
    def test_has_image(
        self, twitter_conn, mock_twitter_api, mock_image, _mock_upload_media
    ):
        twitter_conn.get_api_object.return_value = mock_twitter_api

        twitter_conn = TwitterConnector(fake_token(), fake_token())
        twitter_conn.add_status("this has an image", text_image=mock_image)

        twitter_conn.api_v2.request.assert_called_with(
            "tweets",
            params={
                "text": "this has an image",
                "media": {
                    "media_ids": [
                        "42",
                    ]
                },
            },
            method_override="POST",
        )

    @patch.object(TwitterConnector, "upload_media")
    @patch("bc.core.utils.images.TextImage")
    @patch("TwitterAPI.TwitterAPI.TwitterAPI")
    @patch.object(TwitterConnector, "get_api_object")
    def test_image_alt_text(
        self, twitter_conn, mock_twitter_api, mock_image, mock_upload_media
    ):
        twitter_conn.get_api_object.return_value = mock_twitter_api
        mock_image.description = "the image description"
        mock_image.to_bytes.return_value = "image bytes"

        twitter_conn = TwitterConnector(fake_token(), fake_token())
        twitter_conn.add_status(
            "this has an image",
            text_image=mock_image,
        )
        mock_upload_media.assert_called_with(
            "image bytes",
            "An image of the entry's full text: the image description",
        )

    @patch.object(TwitterConnector, "upload_media", side_effect=[2, 3, 5, 8])
    @patch("TwitterAPI.TwitterAPI.TwitterAPI")
    @patch.object(TwitterConnector, "get_api_object")
    def test_has_thumbnails(
        self, twitter_conn, mock_twitter_api, _mock_upload_media
    ):
        thumb_1 = faker.binary(2)
        thumb_2 = faker.binary(3)
        thumb_3 = faker.binary(5)
        thumb_4 = faker.binary(8)
        twitter_conn.get_api_object.return_value = mock_twitter_api

        twitter_conn = TwitterConnector(fake_token(), fake_token())
        twitter_conn.add_status(
            "this has 4 thumbnails",
            thumbnails=[thumb_1, thumb_2, thumb_3, thumb_4],
        )

        twitter_conn.api_v2.request.assert_called_with(
            "tweets",
            params={
                "text": "this has 4 thumbnails",
                "media": {"media_ids": ["2", "3", "5", "8"]},
            },
            method_override="POST",
        )

    @patch.object(TwitterConnector, "upload_media")
    @patch("TwitterAPI.TwitterAPI.TwitterAPI")
    @patch.object(TwitterConnector, "get_api_object")
    def test_thumbnails_alt_text(
        self, twitter_conn, mock_twitter_api, mock_upload_media
    ):
        twitter_conn.get_api_object.return_value = mock_twitter_api
        thumb_1 = faker.binary(2)
        thumb_2 = faker.binary(3)
        expected_upload_media_calls = [
            call(thumb_1, "Thumbnail of page 1 of the PDF linked above."),
            call(thumb_2, "Thumbnail of page 2 of the PDF linked above."),
        ]

        twitter_conn = TwitterConnector(fake_token(), fake_token())
        twitter_conn.add_status(
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

    @patch("TwitterAPI.TwitterAPI.TwitterAPI")
    @patch.object(TwitterConnector, "get_api_object")
    def test_always_calls_api_v2_request(self, twitter_conn, mock_twitter_api):
        twitter_conn.get_api_object.return_value = mock_twitter_api

        twitter_conn = TwitterConnector(fake_token(), fake_token())
        twitter_conn.add_status("this is the message")

        twitter_conn.api_v2.request.assert_called_with(
            "tweets",
            params={"text": "this is the message"},
            method_override="POST",
        )
