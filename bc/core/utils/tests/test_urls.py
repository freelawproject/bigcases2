from django.conf import settings
from django.test import RequestFactory, SimpleTestCase

from bc.core.utils.urls import (
    BASE_URL,
    get_redirect_or_login_url,
    is_safe_url,
    parse_url_with_ada,
)


class ParseUrlWithAdaTest(SimpleTestCase):
    def test_empty_url(self) -> None:
        self.assertEqual(parse_url_with_ada(""), "")

    def test_relative_url_is_kept_relative(self) -> None:
        self.assertEqual(parse_url_with_ada("/foo/?a=1"), "/foo/?a=1")

    def test_relative_url_is_normalized(self) -> None:
        self.assertEqual(parse_url_with_ada("/foo/../bar/"), "/bar/")
        self.assertEqual(parse_url_with_ada("  /foo/"), "/foo/")

    def test_absolute_url_is_kept(self) -> None:
        self.assertEqual(
            parse_url_with_ada("https://example.com/x"),
            "https://example.com/x",
        )

    def test_base_url_is_stripped(self) -> None:
        self.assertEqual(parse_url_with_ada(f"{BASE_URL}/foo/"), "/foo/")

    def test_scheme_relative_url_becomes_absolute(self) -> None:
        parsed = parse_url_with_ada("//evil.com/x")
        self.assertTrue(parsed.endswith("://evil.com/x"))

    def test_invalid_url_returns_empty_string(self) -> None:
        self.assertEqual(parse_url_with_ada("http://[bad"), "")


class IsSafeUrlTest(SimpleTestCase):
    def setUp(self) -> None:
        self.request = RequestFactory().get("/")

    def test_relative_url_is_safe(self) -> None:
        self.assertTrue(is_safe_url("/subscribe/", self.request))

    def test_empty_url_is_not_safe(self) -> None:
        self.assertFalse(is_safe_url("", self.request))

    def test_external_url_is_not_safe(self) -> None:
        self.assertFalse(is_safe_url("https://evil.com/", self.request))

    def test_javascript_url_is_not_safe(self) -> None:
        self.assertFalse(is_safe_url("javascript:alert(1)", self.request))

    def test_sign_in_and_register_urls_are_not_safe(self) -> None:
        self.assertFalse(is_safe_url("/sign-in/", self.request))
        self.assertFalse(is_safe_url("/register/", self.request))


class GetRedirectOrLoginUrlTest(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_redirect_from_get(self) -> None:
        request = self.factory.get("/", {"next": "/subscribe/"})
        self.assertEqual(
            get_redirect_or_login_url(request, "next"), "/subscribe/"
        )

    def test_redirect_from_post_takes_precedence(self) -> None:
        request = self.factory.post(
            "/?next=/from-get/", {"next": "/from-post/"}
        )
        self.assertEqual(
            get_redirect_or_login_url(request, "next"), "/from-post/"
        )

    def test_missing_redirect_falls_back_to_login_redirect(self) -> None:
        request = self.factory.get("/")
        self.assertEqual(
            get_redirect_or_login_url(request, "next"),
            settings.LOGIN_REDIRECT_URL,
        )

    def test_unsafe_redirects_fall_back_to_login_redirect(self) -> None:
        for url in (
            "https://evil.com/",
            "//evil.com/x",
            "javascript:alert(1)",
            "http://[bad",
        ):
            with self.subTest(url=url):
                request = self.factory.get("/", {"next": url})
                self.assertEqual(
                    get_redirect_or_login_url(request, "next"),
                    settings.LOGIN_REDIRECT_URL,
                )
