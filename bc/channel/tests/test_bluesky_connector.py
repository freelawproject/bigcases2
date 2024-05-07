from unittest.mock import patch

from django.test import SimpleTestCase

from bc.channel.tests.factories import fake_token
from bc.channel.utils.connectors.bluesky import BlueskyConnector


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
