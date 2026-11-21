from http import HTTPStatus
from unittest.mock import patch

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from bc.channel.tests.factories import ChannelFactory
from bc.subscription.models import Subscription
from bc.subscription.tests.factories import SubscriptionFactory
from bc.users.tests.factories import UserFactory


def fake_docket(docket_id: int) -> dict:
    return {
        "id": docket_id,
        "pacer_case_id": "12345",
        "case_name": "United States v. Example",
        "docket_number": "1:23-cv-00001",
        "court_id": "dcd",
        "slug": "united-states-v-example",
    }


@patch("bc.subscription.views.queue")
@patch(
    "bc.subscription.views.lookup_docket_by_cl_id",
    side_effect=fake_docket,
)
class AddCaseViewTest(TestCase):
    def setUp(self) -> None:
        self.curator_channel = ChannelFactory(mastodon=True)
        self.curator = UserFactory(channels=[self.curator_channel])
        self.other_channel = ChannelFactory(mastodon=True)
        self.outsider = UserFactory()
        self.followed = SubscriptionFactory(
            cl_docket_id=999,
            docket_name="Curated name",
            case_summary="Curated summary",
            article_url="https://news.example/story",
            channels=[self.curator_channel],
        )
        self.url = reverse("add_cases")

    def post(self, docket_id: int, channels: list) -> HttpResponse:
        return self.client.post(
            self.url,
            {
                "docketId": docket_id,
                "channels": channels,
                "docket_name": f"ATTACKER NAME {docket_id}",
                "case_summary": "attacker summary",
                "article_url": "https://attacker.example/phish",
            },
        )

    def assert_followed_case_unchanged(self) -> None:
        self.followed.refresh_from_db()
        self.assertEqual(self.followed.docket_name, "Curated name")
        self.assertEqual(self.followed.case_summary, "Curated summary")
        self.assertEqual(
            self.followed.article_url, "https://news.example/story"
        )

    def test_anonymous_user_is_redirected(self, lookup, queue) -> None:
        r = self.post(1000, [self.curator_channel.pk])
        self.assertEqual(r.status_code, HTTPStatus.FOUND)
        self.assertFalse(Subscription.objects.filter(cl_docket_id=1000))

    def test_user_without_channels_cannot_add_case(
        self, lookup, queue
    ) -> None:
        self.client.force_login(self.outsider)

        r = self.post(1000, [self.curator_channel.pk])
        self.assertEqual(r.status_code, HTTPStatus.FORBIDDEN)
        self.assertFalse(Subscription.objects.filter(cl_docket_id=1000))

        r = self.post(999, [self.curator_channel.pk])
        self.assertEqual(r.status_code, HTTPStatus.FORBIDDEN)
        self.assert_followed_case_unchanged()

        # Not even with no channels selected.
        r = self.post(999, [])
        self.assertEqual(r.status_code, HTTPStatus.FORBIDDEN)
        self.assert_followed_case_unchanged()

        lookup.assert_not_called()
        queue.enqueue.assert_not_called()

    def test_curator_cannot_use_channels_they_do_not_curate(
        self, lookup, queue
    ) -> None:
        self.client.force_login(self.curator)

        for channels in (
            [self.other_channel.pk],
            [self.curator_channel.pk, self.other_channel.pk],
            ["not-a-number"],
        ):
            with self.subTest(channels=channels):
                r = self.post(1000, channels)
                self.assertEqual(r.status_code, HTTPStatus.FORBIDDEN)

        self.assertFalse(Subscription.objects.filter(cl_docket_id=1000))
        self.assertFalse(self.other_channel.subscriptions.exists())
        queue.enqueue.assert_not_called()

    def test_curator_must_select_a_channel(self, lookup, queue) -> None:
        self.client.force_login(self.curator)

        r = self.post(999, [])
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "Select at least one channel.")
        self.assert_followed_case_unchanged()
        queue.enqueue.assert_not_called()

    @patch("bc.subscription.services.find_court_by_id", return_value=[])
    def test_curator_can_add_case_to_own_channel(
        self, find_court, lookup, queue
    ) -> None:
        self.client.force_login(self.curator)

        r = self.post(1000, [self.curator_channel.pk])
        self.assertEqual(r.status_code, HTTPStatus.OK)

        subscription = Subscription.objects.get(cl_docket_id=1000)
        self.assertEqual(subscription.docket_name, "ATTACKER NAME 1000")
        self.assertEqual(
            list(subscription.channel.all()), [self.curator_channel]
        )
        self.assertEqual(queue.enqueue.call_count, 2)
