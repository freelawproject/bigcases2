from http import HTTPStatus
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class HealthCheckViewTest(TestCase):
    url = reverse("health_check")

    def test_all_services_up(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json(), {"is_redis_up": True, "is_postgresql_up": True}
        )

    @patch("bc.core.views.check_redis", return_value=False)
    def test_redis_down(self, _mock) -> None:
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR
        )
        self.assertEqual(
            response.json(), {"is_redis_up": False, "is_postgresql_up": True}
        )

    @patch("bc.core.views.check_postgresql", return_value=False)
    def test_postgresql_down(self, _mock) -> None:
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR
        )
        self.assertEqual(
            response.json(), {"is_redis_up": True, "is_postgresql_up": False}
        )
