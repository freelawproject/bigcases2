from django.test import SimpleTestCase

from bc.channel.utils.connectors.masto import get_server_url


class GetServerUrlTest(SimpleTestCase):

    def test_can_get_server_url(self):
        test_inputs = [
            {"handle": "@username@mastodon.social", "server_url": "https://mastodon.social/"},
            {"handle": "@bigcases@law.builders", "server_url": "https://law.builders/"},
            {"handle": "@bottest@mastodon.nl", "server_url": "https://mastodon.nl/"},
        ]

        for test in test_inputs:
            result = get_server_url(test["handle"])
            self.assertEqual(result, test["server_url"])
