from textwrap import wrap

from django.test import SimpleTestCase

from bc.core.utils.images import TextImage


class TextImageTest(SimpleTestCase):
    def test_max_character_count_avoids_overflow(self):
        tests = (
            # Simple case
            {
                "title": "short title",
                "description": 10 * "short description",
                "border_color": (256, 256, 256),
            },
            # Short title and long description
            {
                "title": 5 * "short title",
                "description": 20 * "short description",
                "border_color": (256, 256, 256),
            },
            # Long title and long description
            {
                "title": 15 * "short title",
                "description": 20 * "short description",
                "border_color": (256, 256, 256),
            },
            {
                "title": 30 * "short title",
                "description": 50 * "short description",
                "border_color": (256, 256, 256),
            },
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
                "border_color": (256, 256, 256),
            },
        )

        for test in tests:
            instance = TextImage(**test)
            instance.width, _ = instance.get_initial_dimensions()

            self.assertLessEqual(
                instance.width,
                instance.max_width,
                msg="Failed with dict: %s.\n%s is larger than %s"
                % (test, instance.width, instance.max_width),
            )

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
