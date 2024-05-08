from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from bc.subscription.utils.courtlistener import (
    get_docket_id_from_query,
    is_bankruptcy,
)


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

    @patch("bc.subscription.utils.courtlistener.requests")
    def test_extract_docket_id_from_query(self, mock_requests):
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
            # PDF URL
            {
                "query": "https://storage.courtlistener.com/recap/gov.uscourts.dcd.226485/gov.uscourts.dcd.226485.1.0_6.pdf",
                "docket_id": 41955367,
                "mock_redirect": "https://www.courtlistener.com/docket/41955367/us-dominion-inc-v-giuliani/",
            },
            {
                "query": "https://storage.courtlistener.com/recap/gov.uscourts.ohnd.294863/gov.uscourts.ohnd.294863.15.0.pdf",
                "docket_id": 66817224,
                "mock_redirect": "https://www.courtlistener.com/docket/66817224/canterbury-v-norfolk-southern-corporation/",
            },
        )
        # Create a new Mock to imitate a Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        for test in test_inputs:
            if "mock_redirect" in test:
                mock_response.url = test["mock_redirect"]

            mock_requests.get.return_value = mock_response

            result = get_docket_id_from_query(test["query"])
            self.assertEqual(result, test["docket_id"])


class IsBankruptcyTest(SimpleTestCase):
    def test_is_bankruptcy(self):
        self.assertTrue(is_bankruptcy("13B"))
        self.assertTrue(is_bankruptcy("13b"))

    def test_is_bankruptcy_false(self):
        self.assertFalse(is_bankruptcy("13f"))

    def test_is_bankruptcy_none(self):
        self.assertFalse(is_bankruptcy(None))  # type: ignore
