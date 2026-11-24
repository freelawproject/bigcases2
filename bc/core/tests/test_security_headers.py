from django.test import TestCase
from django.urls import reverse


class SecurityHeadersTest(TestCase):
    """Make sure the security middleware adds the headers we expect.

    These guard against silent regressions when the libraries providing the
    headers change how they are configured (e.g., django-csp 4.0 ignoring the
    old ``CSP_*`` settings).
    """

    def setUp(self) -> None:
        self.response = self.client.get(reverse("homepage"))

    def _csp_directives(self) -> dict[str, list[str]]:
        header = self.response.headers["Content-Security-Policy"]
        directives: dict[str, list[str]] = {}
        for part in header.split(";"):
            name, *values = part.strip().split()
            directives[name] = values
        return directives

    def test_csp_header_is_present(self) -> None:
        self.assertEqual(self.response.status_code, 200)
        self.assertIn("Content-Security-Policy", self.response.headers)
        self.assertNotIn(
            "Content-Security-Policy-Report-Only", self.response.headers
        )

    def test_csp_does_not_upgrade_insecure_requests_in_tests(self) -> None:
        self.assertNotIn("upgrade-insecure-requests", self._csp_directives())

    def test_permissions_policy_header(self) -> None:
        self.assertEqual(
            self.response.headers["Permissions-Policy"], "browsing-topics=()"
        )

    def test_other_security_headers(self) -> None:
        self.assertEqual(self.response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(
            self.response.headers["Referrer-Policy"], "same-origin"
        )
        self.assertEqual(
            self.response.headers["X-Content-Type-Options"], "nosniff"
        )
