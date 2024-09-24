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
                msg="Got wrong status code for page at: {path}. "
                "Status Code: {code}".format(path=path, code=r.status_code),
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
                        msg="'%s' found in HTML of response. This suggests it was "
                        "not cleaned by the sanitize_redirection function."
                        % next_param,
                    )
                else:
                    self.assertIn(
                        f'value="{next_param}"',
                        response.content.decode(),
                        msg="'%s' not found in HTML of response. This suggests it "
                        "was sanitized when it should not have been."
                        % next_param,
                    )
