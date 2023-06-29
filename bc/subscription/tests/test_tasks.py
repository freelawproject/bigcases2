from unittest.mock import MagicMock, patch

from django.test import TestCase

from bc.channel.models import Channel, Post
from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.core.utils.status.templates import (
    TWITTER_FOLLOW_A_NEW_CASE,
    TWITTER_FOLLOW_A_NEW_CASE_W_ARTICLE,
)
from bc.core.utils.tests.base import faker
from bc.sponsorship.tests.factories import SponsorshipFactory
from bc.subscription.models import FilingWebhookEvent
from bc.subscription.tasks import (
    check_webhook_before_posting,
    enqueue_posts_for_docket_alert,
    enqueue_posts_for_new_case,
    make_post_for_webhook_event,
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


class ProcessFetchWebhookEventTest(TestCase):
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


@patch("bc.subscription.tasks.add_sponsored_text_to_thumbnails")
@patch("bc.subscription.tasks.get_thumbnails_from_range")
@patch.object(Channel, "get_api_wrapper")
class MakePostForWebhookEventTest(TestCase):
    webhook_event = None
    webhook_minute_entry = None
    channel = None
    bin_object = None

    @classmethod
    def setUpTestData(cls) -> None:
        subscription = SubscriptionFactory()
        cls.webhook_minute_entry = FilingWebhookEventFactory(
            document_number=None
        )
        cls.webhook_event = FilingWebhookEventFactory(
            doc_id=2974081,
            document_number=2,
            subscription=subscription,
            status=FilingWebhookEvent.WAITING_FOR_DOCUMENT,
        )
        cls.channel = ChannelFactory()
        cls.bin_object = b"\x68\x65\x6c\x6c\x6f"

    def setUp(self) -> None:
        self.status_id = faker.pyint(
            min_value=100_000_000, max_value=900_000_000
        )

    def mock_api_wrapper(self, status_id):
        wrapper = MagicMock()
        wrapper.add_status.return_value = status_id

        return wrapper

    def test_can_create_full_post_no_document(
        self, mock_api, mock_thumbnails, mock_add_sponsor_text
    ):
        mock_api.return_value = self.mock_api_wrapper(self.status_id)

        make_post_for_webhook_event(
            self.channel.pk, self.webhook_event.pk, None
        )
        post = Post.objects.first()

        self.assertEqual(post.object_id, self.status_id)
        self.assertIn("New filing", post.text)
        mock_add_sponsor_text.assert_not_called()
        mock_thumbnails.assert_not_called()

    def test_can_create_minute_entry_no_document(
        self, mock_api, mock_thumbnails, mock_add_sponsor_text
    ):
        mock_api.return_value = self.mock_api_wrapper(self.status_id)

        make_post_for_webhook_event(
            self.channel.pk, self.webhook_minute_entry.pk, None
        )
        post = Post.objects.first()

        self.assertEqual(post.object_id, self.status_id)
        self.assertIn("New minute entry", post.text)

        mock_add_sponsor_text.assert_not_called()
        mock_thumbnails.assert_not_called()

    def test_get_three_thumbnails_from_documents(
        self, mock_api, mock_thumbnails, mock_add_sponsor_text
    ):
        mock_api.return_value = self.mock_api_wrapper(self.status_id)

        # Remove the short description to make sure the template will use the long one
        self.webhook_event.short_description = ""
        self.webhook_event.save(update_fields=["short_description"])

        make_post_for_webhook_event(
            self.channel.pk, self.webhook_event.pk, self.bin_object
        )

        mock_thumbnails.assert_called_with(self.bin_object, "[1,2,3]")
        mock_add_sponsor_text.assert_not_called()

    def test_get_four_thumbnails_from_document(
        self, mock_api, mock_thumbnails, mock_add_sponsor_text
    ):
        mock_api.return_value = self.mock_api_wrapper(self.status_id)

        make_post_for_webhook_event(
            self.channel.pk, self.webhook_event.pk, self.bin_object
        )

        mock_thumbnails.assert_called_with(self.bin_object, "[1,2,3,4]")
        mock_add_sponsor_text.assert_not_called()

    def test_add_sponsor_text_to_thumbails(
        self, mock_api, mock_thumbnails, mock_add_sponsor_text
    ):
        sponsor_text = "This document contributed by Free Law Project"
        mock_api.return_value = self.mock_api_wrapper(self.status_id)
        mock_thumbnails.return_value = [self.bin_object for _ in range(4)]

        make_post_for_webhook_event(
            self.channel.pk,
            self.webhook_event.pk,
            self.bin_object,
            sponsor_text,
        )

        mock_thumbnails.assert_called_with(self.bin_object, "[1,2,3,4]")
        mock_add_sponsor_text.assert_called_with(
            mock_thumbnails(), sponsor_text
        )


@patch("bc.subscription.tasks.lookup_initial_complaint")
@patch("bc.subscription.tasks.Retry")
@patch("bc.subscription.tasks.queue")
@patch.object(Channel, "get_api_wrapper")
class EnqueuePostsForNewCaseTest(TestCase):
    channel = None
    subscription = None
    subscription_w_link = None
    webhook_event = None

    @classmethod
    def setUpTestData(cls) -> None:
        cls.channel = ChannelFactory(twitter=True)
        cls.subscription = SubscriptionFactory(channels=[cls.channel])
        cls.subscription_w_link = SubscriptionFactory(
            article=True, channels=[cls.channel]
        )
        cls.webhook_event = FilingWebhookEventFactory(
            docket_id=65745614,
            doc_id=217368466,
            subscription=cls.subscription,
            status=FilingWebhookEvent.SUCCESSFUL,
        )

    def mock_api_wrapper(self):
        return MagicMock(name="api_wrapper")

    def test_can_enqueue_new_case_status(
        self, mock_api, mock_queue, mock_retry, mock_lookup
    ):
        api_wrapper = self.mock_api_wrapper()
        mock_api.return_value = api_wrapper
        mock_lookup.return_value = None
        message, _ = TWITTER_FOLLOW_A_NEW_CASE.format(
            docket=self.subscription.name_with_summary,
            docket_link=self.subscription.cl_url,
            docket_id=self.subscription.cl_docket_id,
        )

        enqueue_posts_for_new_case(self.subscription.pk)

        mock_queue.enqueue.assert_called_once_with(
            api_wrapper.add_status, message, None, None, retry=mock_retry()
        )

    def test_can_post_new_case_w_link(
        self, mock_api, mock_queue, mock_retry, mock_lookup
    ):
        api_wrapper = self.mock_api_wrapper()
        mock_api.return_value = api_wrapper
        mock_lookup.return_value = None
        message, _ = TWITTER_FOLLOW_A_NEW_CASE_W_ARTICLE.format(
            docket=self.subscription_w_link.name_with_summary,
            docket_link=self.subscription_w_link.cl_url,
            docket_id=self.subscription_w_link.cl_docket_id,
            article_url=self.subscription_w_link.article_url,
        )

        enqueue_posts_for_new_case(self.subscription_w_link.pk)

        mock_queue.enqueue.assert_called_once_with(
            api_wrapper.add_status, message, None, None, retry=mock_retry()
        )

    @patch("bc.subscription.tasks.purchase_pdf_by_doc_id")
    def test_can_purchase_initial_complaint(
        self, mock_purchase, mock_api, mock_queue, mock_retry, mock_lookup
    ):
        api_wrapper = self.mock_api_wrapper()
        mock_api.return_value = api_wrapper

        sponsorship = SponsorshipFactory()
        channel_group = GroupFactory(sponsorships=[sponsorship])
        channel = ChannelFactory(group=channel_group)
        mock_lookup.return_value = {
            "id": 1,
            "filepath_local": "",
            "pacer_doc_id": "051023651280",
        }

        self.subscription.channel.add(channel)

        enqueue_posts_for_new_case(self.subscription.pk)

        mock_purchase.assert_called_once_with(1)
        mock_queue.assert_not_called()

    @patch("bc.subscription.tasks.get_thumbnails_from_range")
    @patch("bc.subscription.tasks.download_pdf_from_cl")
    def test_can_post_new_case_w_thumbnails(
        self,
        mock_download,
        mock_thumbnails,
        mock_api,
        mock_queue,
        mock_retry,
        mock_lookup,
    ):
        api_wrapper = self.mock_api_wrapper()
        mock_api.return_value = api_wrapper
        mock_lookup.return_value = {"filepath_local": faker.url()}

        document = faker.binary(2)
        mock_download.return_value = document

        thumb_1 = faker.binary(4)
        thumb_2 = faker.binary(6)
        mock_thumbnails.return_value = [thumb_1, thumb_2]

        message, _ = TWITTER_FOLLOW_A_NEW_CASE_W_ARTICLE.format(
            docket=self.subscription_w_link.name_with_summary,
            docket_link=self.subscription_w_link.cl_url,
            docket_id=self.subscription_w_link.cl_docket_id,
            article_url=self.subscription_w_link.article_url,
        )

        enqueue_posts_for_new_case(self.subscription_w_link.pk)

        mock_download.assert_called_once()
        mock_thumbnails.assert_called_once_with(document, "[1,2,3,4]")
        mock_queue.enqueue.assert_called_once_with(
            api_wrapper.add_status,
            message,
            None,
            [thumb_1, thumb_2],
            retry=mock_retry(),
        )


@patch("bc.subscription.tasks.Retry")
@patch("bc.subscription.tasks.queue")
@patch.object(Channel, "get_api_wrapper")
class EnqueuePostsForNewFilingTest(TestCase):
    channel = None
    subscription = None
    webhook_event = None

    @classmethod
    def setUpTestData(cls) -> None:
        cls.channel = ChannelFactory(enabled=True, service=Channel.TWITTER)
        cls.subscription = SubscriptionFactory(channels=[cls.channel])
        cls.webhook_event = FilingWebhookEventFactory(
            docket_id=65745614,
            doc_id=217368466,
            subscription=cls.subscription,
            status=FilingWebhookEvent.SUCCESSFUL,
        )

    def mock_api_wrapper(self):
        return MagicMock(name="api_wrapper")

    def test_can_enqueue_new_filing_status(
        self, mock_api, mock_queue, mock_retry
    ):
        mock_api.return_value = self.mock_api_wrapper()

        enqueue_posts_for_docket_alert(self.webhook_event)

        mock_queue.enqueue.assert_called_once_with(
            make_post_for_webhook_event,
            self.channel.pk,
            self.webhook_event.pk,
            None,
            None,
            retry=mock_retry(),
        )
