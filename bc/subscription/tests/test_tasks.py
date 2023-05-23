from unittest.mock import MagicMock, patch

from django.test import TestCase

from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.sponsorship.tests.factories import SponsorshipFactory
from bc.subscription.models import FilingWebhookEvent
from bc.subscription.tasks import (
    check_webhook_before_posting,
    process_fetch_webhook_event,
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


@patch("bc.subscription.tasks.lookup_document_by_doc_id")
class CheckWebhookBeforePostingTest(TestCase):
    webhook_event = None
    subscription = None

    @classmethod
    def setUpTestData(cls) -> None:
        cls.subscription = SubscriptionFactory()
        cls.webhook_event = FilingWebhookEventFactory(
            docket_id=65745614,
            doc_id=217368466,
            subscription=cls.subscription,
            status=FilingWebhookEvent.SUCCESSFUL,
        )

    def test_raise_exception_for_webhook_no_subscription(self, mock_lookup):
        webhook_event_no_subscription = FilingWebhookEventFactory(
            subscription=None, status=FilingWebhookEvent.SUCCESSFUL
        )
        with self.assertRaises(AssertionError):
            check_webhook_before_posting(webhook_event_no_subscription.id)

    def test_ignores_webhook_for_junk_entries(self, mock_lookup):
        webhook_with_junk_entry = FilingWebhookEventFactory(
            subscription=self.subscription,
            status=FilingWebhookEvent.SUCCESSFUL,
            short_description="certificate of disclosure",
        )

        check_webhook_before_posting(webhook_with_junk_entry.id)
        webhook = FilingWebhookEvent.objects.get(id=webhook_with_junk_entry.id)

        self.assertEqual(webhook.status, FilingWebhookEvent.IGNORED)
        mock_lookup.assert_not_called()

    @patch("bc.subscription.tasks.enqueue_posts_for_docket_alert")
    @patch("bc.subscription.tasks.download_pdf_from_cl")
    def test_can_create_post_for_webhook_w_document(
        self, mock_download, mock_enqueue, mock_lookup
    ):
        filepath = "recap/gov.uscourts.mied.365816/gov.uscourts.mied.365816.1.0_12.pdf"
        mock_lookup.return_value = {"filepath_local": filepath}
        mock_download.return_value = b"\x68\x65\x6c\x6c\x6f"

        check_webhook_before_posting(self.webhook_event.id)

        mock_lookup.assert_called_with(self.webhook_event.doc_id)
        mock_download.assert_called_with(filepath)
        mock_enqueue.assert_called_with(self.webhook_event, mock_download())

    @patch("bc.subscription.tasks.enqueue_posts_for_docket_alert")
    @patch("bc.subscription.tasks.download_pdf_from_cl")
    def test_can_create_post_for_webhook_no_document(
        self, mock_download, mock_enqueue, mock_lookup
    ):
        mock_lookup.return_value = {"filepath_local": ""}

        check_webhook_before_posting(self.webhook_event.id)

        mock_lookup.assert_called_with(self.webhook_event.doc_id)
        mock_download.assert_not_called()
        mock_enqueue.assert_called_with(self.webhook_event, None)

    @patch("bc.subscription.tasks.purchase_pdf_by_doc_id")
    @patch("bc.subscription.tasks.download_pdf_from_cl")
    def test_can_start_purchase_for_document(
        self, mock_download, mock_purchase, mock_lookup
    ):
        sponsorship = SponsorshipFactory()
        channel_group = GroupFactory(sponsorships=[sponsorship])
        channel = ChannelFactory(group=channel_group)
        mock_lookup.return_value = {"filepath_local": ""}

        self.subscription.channel.add(channel)

        check_webhook_before_posting(self.webhook_event.id)
        webhook = FilingWebhookEvent.objects.get(id=self.webhook_event.id)

        self.assertEqual(
            webhook.status, FilingWebhookEvent.WAITING_FOR_DOCUMENT
        )
        mock_purchase.assert_called_with(self.webhook_event.doc_id)
        mock_download.assert_not_called()


class ProcessFetchWebhookEvent(TestCase):
    webhook_event = None
    webhook_no_subscription = None

    @classmethod
    def setUpTestData(cls) -> None:
        subscription = SubscriptionFactory()
        cls.webhook_no_subscription = FilingWebhookEventFactory(
            subscription=None
        )
        cls.webhook_event = FilingWebhookEventFactory(
            doc_id=2974081,
            subscription=subscription,
            status=FilingWebhookEvent.WAITING_FOR_DOCUMENT,
        )

    def test_raise_exception_for_webhook_no_subscription(self):
        with self.assertRaises(AssertionError):
            process_fetch_webhook_event(self.webhook_no_subscription.id)

    @patch("bc.subscription.tasks.enqueue_posts_for_docket_alert")
    @patch("bc.subscription.tasks.download_pdf_from_cl")
    @patch("bc.subscription.tasks.lookup_document_by_doc_id")
    def test_can_create_post_after_purchase(
        self, mock_lookup, mock_download, mock_enqueue
    ):
        filepath = (
            "recap/gov.uscourts.dcd.178502/gov.uscourts.dcd.178502.2.0_18.pdf"
        )
        mock_lookup.return_value = {"filepath_local": filepath}
        mock_download.return_value = b"\x68\x65\x6c\x6c\x6f"

        process_fetch_webhook_event(self.webhook_event.id)
        webhook = FilingWebhookEvent.objects.get(id=self.webhook_event.id)

        self.assertEqual(webhook.status, FilingWebhookEvent.SUCCESSFUL)
        mock_lookup.assert_called_with(self.webhook_event.doc_id)
        mock_download.assert_called_with(filepath)
        mock_enqueue.assert_called_with(
            self.webhook_event, mock_download(), True
        )
