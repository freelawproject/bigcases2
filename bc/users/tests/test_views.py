from http import HTTPStatus

from django.test import LiveServerTestCase
from django.urls import reverse


class UserTest(LiveServerTestCase):
    async def test_simple_auth_urls_GET(self) -> None:
        """Can we at least GET all the basic auth URLs?"""
        reverse_names = [
            "sign-in",
            "password_reset",
            "password_reset_done",
            "password_reset_complete",
            "email_confirmation_request",
            "email_confirmation_request_success",
        ]
        for reverse_name in reverse_names:
            path = reverse(reverse_name)
            r = await self.async_client.get(path)
            self.assertEqual(
                r.status_code,
                HTTPStatus.OK,
                msg=f"Got wrong status code for page at: {path}. "
                f"Status Code: {r.status_code}",
            )

    async def test_login_redirects(self) -> None:
        """Do we allow good redirects in login while banning bad ones?"""
        next_params = [
            # A safe redirect
            (reverse("little_cases"), False),
            # Redirection to the register page
            (reverse("register"), True),
            # No open redirects (to a domain outside CL)
            ("https://evil.com&email=e%40e.net", True),
            # No javascript (!)
            ("javascript:confirm(document.domain)", True),
            # No spaces
            ("/test test", True),
            # CRLF injection attack
            (
                "/%0d/evil.com/&email=Your+Account+still+in+maintenance,please+click+Return+below",
                True,
            ),
            # XSS vulnerabilities
            (
                "register/success/?next=java%0d%0ascript%0d%0a:alert(document.cookie)&email=Reflected+XSS+here",
                True,
            ),
        ]
        for next_param, is_not_safe in next_params:
            bad_url = "{host}{path}?next={next}".format(
                host=self.live_server_url,
                path=reverse("sign-in"),
                next=next_param,
            )
            response = await self.async_client.get(bad_url)
            with self.subTest("Checking redirect in login", url=bad_url):
                if is_not_safe:
                    self.assertNotIn(
                        f'value="{next_param}"',
                        response.content.decode(),
                        msg=f"'{next_param}' found in HTML of response. This suggests it was "
                        "not cleaned by the sanitize_redirection function.",
                    )
                else:
                    self.assertIn(
                        f'value="{next_param}"',
                        response.content.decode(),
                        msg=f"'{next_param}' not found in HTML of response. This suggests it "
                        "was sanitized when it should not have been.",
                    )

    async def test_prevent_text_injection_in_success_registration(self):
        """Can we handle text injection attacks?"""
        evil_text = "visit https://evil.com/malware.exe to win $100 giftcard"
        url_params = [
            # A safe redirect and email
            (reverse("little_cases"), "test@free.law", False),
            # Text injection attack
            (reverse("little_cases"), evil_text, True),
            # open redirect and text injection attack
            ("https://evil.com&email=e%40e.net", evil_text, True),
        ]

        for next_param, email, is_evil in url_params:
            url = "{host}{path}?next={next}&email={email}".format(
                host=self.live_server_url,
                path=reverse("register_success"),
                next=next_param,
                email=email,
            )
            response = await self.async_client.get(url)
            with self.subTest("Checking url", url=url):
                if is_evil:
                    self.assertNotIn(
                        email,
                        response.content.decode(),
                        msg=f"'{email}' found in HTML of response. This indicates a "
                        "potential security vulnerability. The view likely "
                        "failed to properly validate it.",
                    )
                else:
                    self.assertIn(
                        email,
                        response.content.decode(),
                        msg=f"'{email}' not found in HTML of response. This suggests a "
                        "a potential issue with the validation logic. The email "
                        "address may have been incorrectly identified as invalid",
                    )
