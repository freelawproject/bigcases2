from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from bc.core.utils.microservices import (
    doctor_auth_headers,
    get_thumbnails_from_range,
)


class DoctorAuthHeadersTest(SimpleTestCase):
    """The doctor bearer token is sent only when it is configured."""

    @override_settings(DOCTOR_AUTH_TOKEN="s3cret")
    def test_token_is_sent(self) -> None:
        self.assertEqual(
            doctor_auth_headers(), {"Authorization": "Bearer s3cret"}
        )

    @override_settings(DOCTOR_AUTH_TOKEN="")
    def test_blank_token_sends_nothing(self) -> None:
        self.assertEqual(doctor_auth_headers(), {})

    @override_settings(DOCTOR_AUTH_TOKEN="s3cret")
    def test_thumbnail_request_carries_it(self) -> None:
        with patch("bc.core.utils.microservices.requests.post") as post:
            post.return_value.content = _EMPTY_ZIP
            get_thumbnails_from_range(b"%PDF-", "[1]")
        post.return_value.raise_for_status.assert_called_once_with()
        self.assertEqual(
            post.call_args.kwargs["headers"],
            {"Authorization": "Bearer s3cret"},
        )


# A zip archive with no members, as get_thumbnails_from_range reads it.
_EMPTY_ZIP = b"PK\x05\x06" + b"\x00" * 18
