from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from .utils.courtlistener import get_docket_id_from_query


class SearchBarTest(SimpleTestCase):
    def test_raises_exception_for_invalid_input(self):
        test_inputs = (
            # Non numeric input
            "ab" * 7,
            # Alphanumeric inputs
            "1a2b3c",
            # Invalid URLS
            "www.google.com",
            "https://twitter.com/home",
            "https://www.courtlistener.com/audio/86390/lac-du-flambeau-band-v-coughlin/",
        )

        for query in test_inputs:
            with self.assertRaises(ValidationError):
                get_docket_id_from_query(query)

    def test_extract_docket_id_from_query(self):
        test_inputs = (
            # Simple case, numeric input
            {"query": "15", "docket_id": 15},
            # CL docket URL
            {
                "query": "https://www.courtlistener.com/docket/59964540/goodluck-v-biden-jr/",
                "docket_id": 59964540,
            },
            {
                "query": "https://www.courtlistener.com/docket/65745614/united-states-v-ward/",
                "docket_id": 65745614,
            },
            {
                "query": "https://www.courtlistener.com/docket/65895581/carroll-v-trump/",
                "docket_id": 65895581,
            },
            # CL document URL
            {
                "query": "https://www.courtlistener.com/docket/65364032/6/1/antonyuk-v-hochul/",
                "docket_id": 65364032,
            },
            {
                "query": "https://www.courtlistener.com/docket/65680829/7/cornet-v-twitter-inc/",
                "docket_id": 65680829,
            },
        )
        for test in test_inputs:
            result = get_docket_id_from_query(test["query"])
            self.assertEqual(result, test["docket_id"])
