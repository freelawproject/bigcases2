import re
from unittest.mock import patch

from django.test import SimpleTestCase

from bc.channel.tests.factories import fake_token
from bc.channel.utils.connectors.bluesky_api.client import BlueskyAPI
from bc.core.utils.status.templates import (
    BLUESKY_FOLLOW_A_NEW_CASE,
    MASTODON_FOLLOW_A_NEW_CASE,
    TWITTER_FOLLOW_A_NEW_CASE,
    THREADS_FOLLOW_A_NEW_CASE,
    MastodonTemplate,
)
from bc.core.utils.tests.base import faker


class NewSubscriptionValidTemplateTest(SimpleTestCase):
    def setUp(self) -> None:
        self.docket_url = "https://www.courtlistener.com/docket/68073028/01208579363/united-states-v-donald-trump/?redirect_or_modal=True"
        self.initial_complaint_link = "https://www.courtlistener.com/opinion/9472375/united-states-v-donald-trump/"
        self.article_url = "https://www.theverge.com/2023/9/11/23868870/internet-archive-hachette-open-library-copyright-lawsuit-appeal"
        self.docket_id = "68073028"
        self.date_filed = "2023-12-13"
        self.initial_complaint_type = (
            "Bankruptcy"  # Use this title since it's the longest possible one
        )
        return super().setUp()

    def test_check_output_validity_mastodon_simple_template(self):
        template = MASTODON_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 47]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [48, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_mastodon_template_w_article(self):
        template = MASTODON_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [41, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_mastodon_template_w_date(self):
        template = MASTODON_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 43]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [44, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_mastodon_template_w_initial_complaint(self):
        template = MASTODON_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 39]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_mastodon_template_w_article_date(self):
        template = MASTODON_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 36]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [37, 40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                )
                self.assertFalse(template.is_valid)

    def test_check_output_validity_mastodon_template_w_article_initial_complaint(
        self,
    ):
        template = MASTODON_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 32]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [33, 40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_mastodon_template_w_article_date_initial_complaint(
        self,
    ):
        template = MASTODON_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 24, 26, 28]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [30, 40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                    article_url=self.article_url,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_mastodon_template_w_date_initial_complaint(
        self,
    ):
        template = MASTODON_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 35]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [36, 40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_twitter_simple_template(self):
        template = TWITTER_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 43]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [44, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_twitter_template_w_article(self):
        template = TWITTER_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 36]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [37, 40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_twitter_template_w_date(self):
        template = TWITTER_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 39]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_twitter_template_w_initial_complaint(self):
        template = TWITTER_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 35]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [36, 40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_twitter_template_w_article_date(self):
        template = TWITTER_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 32]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [33, 40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_twitter_template_w_article_initial_complaint(
        self,
    ):
        template = TWITTER_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 28]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [29, 40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_twitter_template_w_article_date_initial_complaint(
        self,
    ):
        template = TWITTER_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 25]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [26, 40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_twitter_template_w_date_initial_complaint(
        self,
    ):
        template = TWITTER_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 31]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [32, 40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_bluesky_simple_template(self):
        template = BLUESKY_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 50, 50]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [51, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_bluesky_template_w_article(self):
        template = BLUESKY_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 46]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [47, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_bluesky_template_w_date(self):
        template = BLUESKY_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 46]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [47, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_bluesky_template_w_initial_complaint(self):
        template = BLUESKY_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 47]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [48, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_bluesky_template_w_article_date(self):
        template = BLUESKY_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 42]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [43, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_bluesky_template_w_article_initial_complaint(
        self,
    ):
        template = BLUESKY_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 43]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [44, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_bluesky_template_w_date_initial_complaint(
        self,
    ):
        template = BLUESKY_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 43]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [44, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)

    def test_check_output_validity_bluesky_template_w_article_date_initial_complaint(
        self,
    ):
        template = BLUESKY_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 39]
        for multiplier in valid_multipliers:
            with self.subTest(multiplier=multiplier, valid=True):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertTrue(template.is_valid)

        invalid_multipliers = [40, 50, 100]
        for multiplier in invalid_multipliers:
            with self.subTest(multiplier=multiplier, valid=False):
                template.format(
                    docket=multiplier * "short",
                    docket_link=self.docket_url,
                    docket_id=self.docket_id,
                    article_url=self.article_url,
                    date_filed=self.date_filed,
                    initial_complaint_type=self.initial_complaint_type,
                    initial_complaint_link=self.initial_complaint_link,
                )

                self.assertFalse(template.is_valid)


class MastodonTemplateTest(SimpleTestCase):
    def test_count_fixed_characters(self):
        template_with_breaks = (
            "New filing in {docket}\n"
            "Doc #{doc_num}: {description}\n\n"
            "PDF: {pdf_link}\n"
            "Docket: {docket_link}"
        )
        tests = (
            # Simple case
            {"length": 15, "template": "No placerholder"},
            # Include placeholders
            {"length": 0, "template": "{test}"},
            {"length": 0, "template": "{test}{test_2}{test_3}"},
            {"length": 1, "template": "{test} {test_2}"},
            # Include placeholders + text
            {"length": 17, "template": "One placerholder {test}"},
            {"length": 19, "template": "Two placerholders {test}:{test}"},
            {"length": 38, "template": template_with_breaks},
        )

        for test in tests:
            test_class = MastodonTemplate(
                link_placeholders=[], str_template=test["template"]
            )
            result = test_class.count_fixed_characters()
            self.assertEqual(
                result,
                test["length"],
                msg="Failed with dict: %s.\n%s is longer than %s"
                % (test, result, test["length"]),
            )

    def test_compute_length_of_template_with_links(self):
        tests = (
            # Simple case
            {"length": 8, "template": "No links", "links": []},
            # Include links
            {"length": 23, "template": "{link_1}", "links": ["link_1"]},
            {
                "length": 9 + 23,
                "template": "One link {link_1}",
                "links": ["link_1"],
            },
            {
                "length": 11 + 23 * 2,
                "template": "Two links {link_1}:{link_2}",
                "links": ["link_1", "link_2"],
            },
            {
                "length": 23 * 3,
                "template": "{link_1}{link_2}{link_3}",
                "links": ["link_1", "link_2", "link_3"],
            },
            # Include links and placeholder
            {
                "length": 18 + 23,
                "template": "link+placeholder {title}:{description}{link}",
                "links": ["link"],
            },
        )

        for test in tests:
            test_class = MastodonTemplate(
                link_placeholders=test["links"], str_template=test["template"]
            )
            result = len(test_class)
            self.assertEqual(
                result,
                test["length"],
                msg="Failed with dict: %s.\n%s is longer than %s"
                % (test, result, test["length"]),
            )

    def test_truncate_descriptions(self):
        template = MastodonTemplate(
            link_placeholders=["link"], str_template="{title}:{description}"
        )

        tests = (
            # Simple case
            {"title": "short title", "description": "short description"},
            {"title": "short title", "description": 50 * "short"},
            {"title": "short title", "description": 90 * "short"},
            {"title": "short title", "description": 101 * "short"},
            {"title": "short title", "description": 200 * "short"},
        )
        for test in tests:
            result, _ = template.format(**test)
            self.assertTrue(
                len(result) <= template.max_characters,
                msg="Failed with dict: %s.\n%s is longer than %s"
                % (test, result, template.max_characters),
            )


class BlueskyTemplateTest(SimpleTestCase):

    @patch(
        "bc.channel.utils.connectors.bluesky_api.client.BlueskyAPI._get_session"
    )
    def test_create_posts_with_no_brackets(self, mock_session):
        fake_article_url = faker.url()
        fake_docket_url = faker.url()
        fake_initial_complaint_link = faker.url()

        message, _ = BLUESKY_FOLLOW_A_NEW_CASE.format(
            docket=faker.text(),
            docket_link=fake_docket_url,
            docket_id=faker.random_int(100_000, 400_000),
            article_url=fake_article_url,
            date_filed=None,
            initial_complaint_type="Complaint",
            initial_complaint_link=fake_initial_complaint_link,
        )
        bluesky_connector = BlueskyAPI(fake_token(), fake_token())
        post_content = bluesky_connector._clean_text(message)
        # This regular expression ensures that no brackets are included in
        # the content of the post to enclose embedded links
        pattern = r"View Full Case | Complaint | Context"
        self.assertIsNotNone(re.search(pattern, post_content))


class NoEscapeTemplateTest(SimpleTestCase):

    def test_mastodon_follow_new_case_template_no_escape(self):
        fake_docket_link = faker.url()
        fake_docket_id = faker.random_int(100_000, 400_000)
        message, _ = MASTODON_FOLLOW_A_NEW_CASE.format(
            docket="someone's case",
            docket_link=fake_docket_link,
            docket_id=fake_docket_id,
        )
        correct_message = """I'm now following someone's case:

Docket: {docket_link}

#CL{docket_id}""".format(docket_link=fake_docket_link,
            docket_id=fake_docket_id)

        self.assertEqual(message, correct_message)


    def test_twitter_follow_new_case_template_no_escape(self):
        fake_docket_url = faker.url()
        fake_docket_id = faker.random_int(100_000, 400_000)

        message, _ = TWITTER_FOLLOW_A_NEW_CASE.format(
            docket="someone's case",
            docket_link=fake_docket_url,
            docket_id=fake_docket_id,
        )

        correct_message = """I'm now following someone's case:

Docket: {docket_link}

#CL{docket_id}""".format(docket_link=fake_docket_url,
            docket_id=fake_docket_id,)

        self.assertEqual(message, correct_message)


    def test_bluesky_follow_new_case_template_no_escape(self):
        fake_docket_url = faker.url()
        fake_docket_id = faker.random_int(100_000, 400_000)

        message, _ = BLUESKY_FOLLOW_A_NEW_CASE.format(
            docket="someone's case",
            docket_link=fake_docket_url,
            docket_id=fake_docket_id,
        )

        correct_message = """I'm now following someone's case:

[View Full Case]({docket_link})

#CL{docket_id}""".format(docket_link=fake_docket_url,
            docket_id=fake_docket_id,)

        self.assertEqual(message, correct_message)


    def test_threads_follow_new_case_template_no_escape(self):
        fake_docket_url = faker.url()
        fake_docket_id = faker.random_int(100_000, 400_000)

        message, _ = THREADS_FOLLOW_A_NEW_CASE.format(
            docket="someone's case",
            docket_link=fake_docket_url,
            docket_id=fake_docket_id,
        )

        correct_message = """I'm now following someone's case:

Docket: {docket_link}

#CL{docket_id}""".format(docket_link=fake_docket_url,
            docket_id=fake_docket_id,)

        self.assertEqual(message, correct_message)
