from http import HTTPStatus
from unittest.mock import patch

import redis
from django.db import OperationalError
from django.test import TestCase
from django.urls import reverse

from bc.core.utils.connections import check_postgresql, check_redis


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


class ConnectionChecksTest(TestCase):
    def test_check_redis_up(self) -> None:
        self.assertTrue(check_redis())

    @patch("redis.Redis.ping", side_effect=redis.exceptions.ConnectionError)
    def test_check_redis_connection_error(self, _mock) -> None:
        self.assertFalse(check_redis())

    @patch("redis.Redis.ping", side_effect=ConnectionRefusedError)
    def test_check_redis_connection_refused(self, _mock) -> None:
        self.assertFalse(check_redis())

    def test_check_postgresql_up(self) -> None:
        self.assertTrue(check_postgresql())

    @patch(
        "django.db.backends.utils.CursorWrapper.execute",
        side_effect=OperationalError,
    )
    def test_check_postgresql_down(self, _mock) -> None:
        self.assertFalse(check_postgresql())
