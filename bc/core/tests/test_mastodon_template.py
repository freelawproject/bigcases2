from textwrap import wrap

from django.test import SimpleTestCase

from bc.core.utils.status.templates import (
    BLUESKY_FOLLOW_A_NEW_CASE,
    BLUESKY_FOLLOW_A_NEW_CASE_W_ARTICLE,
    MASTODON_FOLLOW_A_NEW_CASE,
    MASTODON_FOLLOW_A_NEW_CASE_W_ARTICLE,
    TWITTER_FOLLOW_A_NEW_CASE,
    TWITTER_FOLLOW_A_NEW_CASE_W_ARTICLE,
    MastodonTemplate,
)


class NewSubscriptionValidTemplateTest(SimpleTestCase):
    def setUp(self) -> None:
        self.docket_url = "https://www.courtlistener.com/docket/68073028/01208579363/united-states-v-donald-trump/?redirect_or_modal=True"
        self.article_url = "https://www.theverge.com/2023/9/11/23868870/internet-archive-hachette-open-library-copyright-lawsuit-appeal"
        self.docket_id = "68073028"
        return super().setUp()

    def test_check_output_validity_mastodon_simple_template(self):
        template = MASTODON_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 48]
        for multiplier in valid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )
            self.assertTrue(template.is_valid)

        invalid_multipliers = [50, 100]
        for multiplier in invalid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )
            self.assertFalse(template.is_valid)

    def test_check_output_validity_mastodon_template_w_article(self):
        template = MASTODON_FOLLOW_A_NEW_CASE_W_ARTICLE
        valid_multipliers = [5, 10, 20, 40]
        for multiplier in valid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )

            self.assertTrue(template.is_valid)

        invalid_multipliers = [41, 50, 100]
        for multiplier in invalid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )
            self.assertFalse(template.is_valid)

    def test_check_output_validity_twitter_simple_template(self):
        template = TWITTER_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 44]
        for multiplier in valid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )
            self.assertTrue(template.is_valid)

        invalid_multipliers = [45, 50, 100]
        for multiplier in invalid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )
            self.assertFalse(template.is_valid)

    def test_check_output_validity_twitter_template_w_article(self):
        template = TWITTER_FOLLOW_A_NEW_CASE_W_ARTICLE
        valid_multipliers = [5, 10, 20, 35]
        for multiplier in valid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )
            self.assertTrue(template.is_valid)

        invalid_multipliers = [37, 50, 100]
        for multiplier in invalid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )
            self.assertFalse(template.is_valid)

    def test_check_output_validity_bluesky_simple_template(self):
        template = BLUESKY_FOLLOW_A_NEW_CASE
        valid_multipliers = [5, 10, 20, 40, 50]
        for multiplier in valid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )
            self.assertTrue(template.is_valid)

        invalid_multipliers = [51, 100]
        for multiplier in invalid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )
            self.assertFalse(template.is_valid)

    def test_check_output_validity_bluesky_template_w_article(self):
        template = BLUESKY_FOLLOW_A_NEW_CASE_W_ARTICLE
        valid_multipliers = [5, 10, 20, 40, 46]
        for multiplier in valid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
            )
            self.assertTrue(template.is_valid)

        invalid_multipliers = [47, 50, 100]
        for multiplier in invalid_multipliers:
            template.format(
                docket=multiplier * "short",
                docket_link=self.docket_url,
                docket_id=self.docket_id,
                article_url=self.article_url,
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
