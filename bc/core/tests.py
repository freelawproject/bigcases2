from textwrap import wrap
from unittest import TestCase

from bc.core.utils.images import TextImage
from bc.core.utils.status.templates import MastodonTemplate


class MastodonTemplateTest(TestCase):
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


class TextImageTest(TestCase):
    tests = (
        # Simple case
        {"title": "short title", "description": 10 * "short description"},
        # Short title and long description
        {"title": 5 * "short title", "description": 20 * "short description"},
        # Long title and long description
        {"title": 15 * "short title", "description": 20 * "short description"},
        {"title": 30 * "short title", "description": 50 * "short description"},
    )

    def test_creates_canvas_smaller_than_max_width(self):
        for test in self.tests:
            instance = TextImage(**test)
            width, _ = instance.get_initial_dimensions()
            self.assertLessEqual(
                width,
                instance.max_width,
                msg="Failed with dict: %s.\n%s is larger than %s"
                % (test, width, instance.max_width),
            )

    def test_max_character_count_avoids_overflow(self):
        EDGE_CASE = (
            {
                "title": (
                    "Case: Braidwood Management v. Becerra (ACA prev. care"
                    " challenge)"
                ),
                "description": (
                    "Transcript Order Form: re 115 Notice of Appeal,,,,"
                    " transcript not requested Reminder: If the transcript is"
                    " ordered for an appeal, Appellant must also file a copy"
                    " of the order form with the appeals court. (Lynch,"
                    " Christopher) (Entered: 04/10/2023)"
                ),
            },
        )

        for test in self.tests + EDGE_CASE:
            instance = TextImage(**test)
            instance.width, _ = instance.get_initial_dimensions()

            # compute the max number of character to render in each line
            max_character = instance.get_max_character_count()

            # wrap the title and description using the max_character variable
            wrapped_title = wrap(instance.title, max_character)
            wrapped_desc = wrap(instance.description, max_character)

            # check if the title overflows the canvas
            self.assertGreaterEqual(
                instance.get_available_space(wrapped_title),
                0,
                msg=f"Failed with dict: {test}.\nthe title overflows the image",
            )

            # check if the description overflows the canvas
            self.assertGreaterEqual(
                instance.get_available_space(wrapped_desc),
                0,
                msg=f"Failed with dict: {test}.\nthe description overflows the image",
            )
