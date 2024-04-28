from typing import cast

from django.test import SimpleTestCase

from bc.channel.models import Channel, Post


class ModelsUrlTest(SimpleTestCase):
    def setUp(self) -> None:
        self.bluesky_channel = Channel(
            service=Channel.BLUESKY, account="bigcases.bots.law"
        )
        self.mastodon_channel = Channel(
            service=Channel.MASTODON, account="@bigcases@law.builders"
        )
        self.twitter_channel = Channel(
            service=Channel.TWITTER, account="big_cases"
        )

    def test_self_url(self) -> None:
        test_cases = [
            {
                "channel": self.bluesky_channel,
                "expected_url": "https://bsky.app/profile/bigcases.bots.law",
            },
            {
                "channel": self.mastodon_channel,
                "expected_url": "https://law.builders/@bigcases",
            },
            {
                "channel": self.twitter_channel,
                "expected_url": "https://twitter.com/big_cases",
            },
        ]

        for test in test_cases:
            with self.subTest(test=test):
                channel = cast(Channel, test["channel"])
                self_url = channel.self_url()
                self.assertEqual(self_url, test["expected_url"])

    def test_post_url(self) -> None:
        test_cases = [
            {
                "channel": self.bluesky_channel,
                "expected_url": "https://bsky.app/profile/bigcases.bots.law/post/12345",
            },
            {
                "channel": self.mastodon_channel,
                "expected_url": "https://law.builders/@bigcases/12345",
            },
            {
                "channel": self.twitter_channel,
                "expected_url": "https://twitter.com/big_cases/status/12345",
            },
        ]

        for test in test_cases:
            with self.subTest(test=test):
                channel = cast(Channel, test["channel"])
                post = Post(
                    channel=channel,
                    object_id="12345",
                )

                post_url = post.post_url
                self.assertEqual(post_url, test["expected_url"])
