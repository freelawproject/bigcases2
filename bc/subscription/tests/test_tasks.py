from unittest.mock import MagicMock, patch

from django.test import TestCase

from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.sponsorship.tests.factories import SponsorshipFactory
from bc.subscription.models import FilingWebhookEvent
from bc.subscription.tasks import (
    check_webhook_before_posting,
    process_filing_webhook_event,
)

from .factories import FilingWebhookEventFactory, SubscriptionFactory


class ProcessFilingWebhookEventTest(TestCase):
    webhook_event = None
    webhook_event_n_subscription = None
    subscription = None

    @classmethod
    def setUpTestData(cls) -> None:
        cls.subscription = SubscriptionFactory()
        cls.webhook_event = FilingWebhookEventFactory(
            docket_id=cls.subscription.cl_docket_id,
        )
        cls.webhook_event_n_subscription = FilingWebhookEventFactory()

    def test_can_match_webhook_and_subscription(self):
        process_filing_webhook_event(self.webhook_event.pk)

        webhook = FilingWebhookEvent.objects.get(id=self.webhook_event.id)
        self.assertEqual(webhook.subscription_id, self.subscription.id)
        self.assertEqual(webhook.status, FilingWebhookEvent.SUCCESSFUL)

    def test_handle_webhooks_with_no_subscription(self):
        process_filing_webhook_event(self.webhook_event_n_subscription.pk)
        webhook = FilingWebhookEvent.objects.get(
            id=self.webhook_event_n_subscription.id
        )
        self.assertEqual(webhook.status, FilingWebhookEvent.FAILED)
