from unittest.mock import MagicMock, call, patch

from django.test import TestCase

from bc.channel.models import Channel, Post
from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.core.utils.status.templates import (
    BLUESKY_FOLLOW_A_NEW_CASE,
    MASTODON_FOLLOW_A_NEW_CASE,
)
from bc.core.utils.tests.base import faker
from bc.sponsorship.tests.factories import SponsorshipFactory
from bc.subscription.models import FilingWebhookEvent
from bc.subscription.tasks import (
    check_initial_complaint_before_posting,
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
    def test_can_create_post_for_webhook_w_document(
        self, mock_enqueue, mock_lookup
    ):
        filepath = "recap/gov.uscourts.mied.365816/gov.uscourts.mied.365816.1.0_12.pdf"
        mock_lookup.return_value = {"filepath_local": filepath}

        check_webhook_before_posting(self.webhook_event.id)
        mock_lookup.assert_called_with(self.webhook_event.doc_id)
        mock_enqueue.assert_called_with(self.webhook_event, filepath)

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
        channel = ChannelFactory(mastodon=True, group=channel_group)
        mock_lookup.return_value = {"filepath_local": ""}

        self.subscription.channel.add(channel)

        check_webhook_before_posting(self.webhook_event.id)
        webhook = FilingWebhookEvent.objects.get(id=self.webhook_event.id)

        self.assertEqual(
            webhook.status, FilingWebhookEvent.WAITING_FOR_DOCUMENT
        )
        mock_purchase.assert_called_with(
            self.webhook_event.doc_id, self.webhook_event.docket_id
        )
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
    @patch("bc.subscription.tasks.lookup_document_by_doc_id")
    def test_can_create_post_after_purchase(self, mock_lookup, mock_enqueue):
        filepath = (
            "recap/gov.uscourts.dcd.178502/gov.uscourts.dcd.178502.2.0_18.pdf"
        )
        mock_lookup.return_value = {
            "filepath_local": filepath,
            "page_count": 1,
        }

        process_fetch_webhook_event(self.webhook_event.id)
        webhook = FilingWebhookEvent.objects.get(id=self.webhook_event.id)

        self.assertEqual(webhook.status, FilingWebhookEvent.SUCCESSFUL)
        mock_lookup.assert_called_with(self.webhook_event.doc_id)
        mock_enqueue.assert_called_with(self.webhook_event, filepath, True)


@patch("bc.subscription.tasks.add_sponsored_text_to_thumbnails")
@patch("bc.subscription.tasks.get_thumbnails_from_range")
@patch.object(Channel, "get_api_wrapper")
@patch("bc.subscription.tasks.download_pdf_from_cl")
class MakePostForWebhookEventTest(TestCase):
    webhook_event = None
    webhook_minute_entry = None
    channel = None
    bin_object = None
    fake_document_path = None

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
        cls.channel = ChannelFactory(mastodon=True)
        cls.bin_object = b"\x68\x65\x6c\x6c\x6f"
        cls.fake_document_path = faker.url()

    def setUp(self) -> None:
        self.status_id = str(
            faker.pyint(min_value=100_000_000, max_value=900_000_000)
        )

    def mock_api_wrapper(self, status_id):
        wrapper = MagicMock()
        wrapper.add_status.return_value = status_id

        return wrapper

    def test_can_create_full_post_no_document(
        self, mock_download, mock_api, mock_thumbnails, mock_add_sponsor_text
    ):
        mock_api.return_value = self.mock_api_wrapper(self.status_id)

        make_post_for_webhook_event(
            self.channel.pk, self.webhook_event.pk, None
        )
        post = Post.objects.first()

        self.assertEqual(post.object_id, self.status_id)
        self.assertIn("New filing", post.text)
        mock_download.assert_not_called()
        mock_add_sponsor_text.assert_not_called()
        mock_thumbnails.assert_not_called()

    def test_can_create_minute_entry_no_document(
        self, mock_download, mock_api, mock_thumbnails, mock_add_sponsor_text
    ):
        mock_api.return_value = self.mock_api_wrapper(self.status_id)

        make_post_for_webhook_event(
            self.channel.pk, self.webhook_minute_entry.pk, None
        )
        post = Post.objects.first()

        self.assertEqual(post.object_id, self.status_id)
        self.assertIn("New minute entry", post.text)

        mock_download.assert_not_called()
        mock_add_sponsor_text.assert_not_called()
        mock_thumbnails.assert_not_called()

    def test_get_three_thumbnails_from_documents(
        self, mock_download, mock_api, mock_thumbnails, mock_add_sponsor_text
    ):
        mock_api.return_value = self.mock_api_wrapper(self.status_id)

        # Remove the short description to make sure the template will use the long one
        self.webhook_event.short_description = ""
        self.webhook_event.save(update_fields=["short_description"])

        # This test case verifies that `make_post_for_webhook_event` can handle
        # document URLs as input, in contrast to the previous test that used
        # URLs.
        mock_download.return_value = self.bin_object
        make_post_for_webhook_event(
            self.channel.pk, self.webhook_event.pk, self.fake_document_path
        )

        mock_download.assert_called_once_with(self.fake_document_path)
        mock_thumbnails.assert_called_with(self.bin_object, "[1,2,3]")
        mock_add_sponsor_text.assert_not_called()

    def test_get_four_thumbnails_from_document(
        self, mock_download, mock_api, mock_thumbnails, mock_add_sponsor_text
    ):
        mock_api.return_value = self.mock_api_wrapper(self.status_id)
        mock_download.return_value = self.bin_object

        make_post_for_webhook_event(
            self.channel.pk, self.webhook_event.pk, self.fake_document_path
        )
        mock_download.assert_called_once_with(self.fake_document_path)
        mock_thumbnails.assert_called_with(self.bin_object, "[1,2,3,4]")
        mock_add_sponsor_text.assert_not_called()

    def test_add_sponsor_text_to_thumbails(
        self, mock_download, mock_api, mock_thumbnails, mock_add_sponsor_text
    ):
        sponsor_text = "This document contributed by Free Law Project"
        mock_api.return_value = self.mock_api_wrapper(self.status_id)
        mock_thumbnails.return_value = [self.bin_object for _ in range(4)]
        mock_download.return_value = self.bin_object

        make_post_for_webhook_event(
            self.channel.pk,
            self.webhook_event.pk,
            self.fake_document_path,
            sponsor_text,
        )

        mock_download.assert_called_once_with(self.fake_document_path)
        mock_thumbnails.assert_called_with(self.bin_object, "[1,2,3,4]")
        mock_add_sponsor_text.assert_called_with(
            mock_thumbnails(), sponsor_text
        )


@patch("bc.subscription.tasks.lookup_initial_complaint")
@patch("bc.subscription.tasks.lookup_docket_by_cl_id")
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
        cls.channel = ChannelFactory(bluesky=True)
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

    @patch("bc.subscription.tasks.enqueue_posts_for_new_case")
    @patch("bc.subscription.tasks.download_pdf_from_cl")
    def test_can_create_new_post_wo_document(
        self,
        mock_download,
        mock_enqueue,
        mock_api,
        mock_queue,
        mock_retry,
        mock_docket_by_cl_id,
        mock_lookup,
    ):
        mock_lookup.return_value = {
            "id": 1,
            "filepath_local": "",
            "pacer_doc_id": "051023651280",
        }

        check_initial_complaint_before_posting(self.subscription.pk)

        mock_lookup.assert_called_once_with(self.subscription.cl_docket_id)
        mock_download.assert_not_called()
        mock_enqueue.assert_called_once_with(
            self.subscription, None, initial_document=mock_lookup.return_value
        )

    @patch("bc.subscription.tasks.enqueue_posts_for_new_case")
    def test_can_download_initial_complaint(
        self,
        mock_enqueue,
        mock_api,
        mock_queue,
        mock_retry,
        mock_docket_by_cl_id,
        mock_lookup,
    ):
        local_filepath = faker.url()
        mock_lookup.return_value = {
            "id": 1,
            "filepath_local": local_filepath,
            "pacer_doc_id": "051023651280",
        }

        check_initial_complaint_before_posting(self.subscription.pk)
        mock_lookup.assert_called_once_with(self.subscription.cl_docket_id)
        mock_enqueue.assert_called_once_with(
            self.subscription,
            local_filepath,
            initial_document=mock_lookup.return_value,
        )

    @patch("bc.subscription.tasks.purchase_pdf_by_doc_id")
    def test_can_purchase_initial_complaint(
        self,
        mock_purchase,
        mock_api,
        mock_queue,
        mock_retry,
        mock_docket_by_cl_id,
        mock_lookup,
    ):
        api_wrapper = self.mock_api_wrapper()
        mock_api.return_value = api_wrapper

        sponsorship = SponsorshipFactory()
        channel_group = GroupFactory(sponsorships=[sponsorship])
        channel = ChannelFactory(mastodon=True, group=channel_group)

        mock_lookup.return_value = {
            "id": 1,
            "filepath_local": "",
            "pacer_doc_id": "051023651280",
        }

        self.subscription.channel.add(channel)

        check_initial_complaint_before_posting(self.subscription.pk)

        mock_purchase.assert_called_once_with(
            1, self.subscription.cl_docket_id
        )
        mock_queue.assert_not_called()

    def test_can_enqueue_new_case_status(
        self,
        mock_api,
        mock_queue,
        mock_retry,
        mock_docket_by_cl_id,
        mock_lookup,
    ):
        api_wrapper = self.mock_api_wrapper()
        mock_api.return_value = api_wrapper
        mock_lookup.return_value = None
        mock_docket_by_cl_id.return_value = None
        message, _ = BLUESKY_FOLLOW_A_NEW_CASE.format(
            docket=self.subscription.name_with_summary,
            docket_link=self.subscription.cl_url,
            docket_id=self.subscription.cl_docket_id,
        )

        enqueue_posts_for_new_case(self.subscription)

        mock_queue.enqueue.assert_called_once_with(
            api_wrapper.add_status, message, None, None, retry=mock_retry()
        )

    def test_can_post_new_case_w_link(
        self,
        mock_api,
        mock_queue,
        mock_retry,
        mock_docket_by_cl_id,
        mock_lookup,
    ):
        api_wrapper = self.mock_api_wrapper()
        mock_api.return_value = api_wrapper
        mock_lookup.return_value = None
        mock_docket_by_cl_id.return_value = None
        message, _ = BLUESKY_FOLLOW_A_NEW_CASE.format(
            docket=self.subscription_w_link.name_with_summary,
            docket_link=self.subscription_w_link.cl_url,
            docket_id=self.subscription_w_link.cl_docket_id,
            article_url=self.subscription_w_link.article_url,
        )
        enqueue_posts_for_new_case(self.subscription_w_link)

        mock_queue.enqueue.assert_called_once_with(
            api_wrapper.add_status, message, None, None, retry=mock_retry()
        )

    @patch("bc.subscription.tasks.get_thumbnails_from_range")
    @patch("bc.subscription.tasks.download_pdf_from_cl")
    def test_can_post_new_case_w_thumbnails(
        self,
        mock_download_pdf,
        mock_thumbnails,
        mock_api,
        mock_queue,
        mock_retry,
        mock_docket_by_cl_id,
        mock_lookup,
    ):
        api_wrapper = self.mock_api_wrapper()
        mock_api.return_value = api_wrapper

        mock_lookup.return_value = None
        mock_docket_by_cl_id.return_value = None

        document = faker.binary(2)

        thumb_1 = faker.binary(4)
        thumb_2 = faker.binary(6)
        mock_thumbnails.return_value = [thumb_1, thumb_2]
        mock_download_pdf.return_value = document
        message, _ = BLUESKY_FOLLOW_A_NEW_CASE.format(
            docket=self.subscription_w_link.name_with_summary,
            docket_link=self.subscription_w_link.cl_url,
            docket_id=self.subscription_w_link.cl_docket_id,
            article_url=self.subscription_w_link.article_url,
        )

        # This test case verifies the handling of document URLs.
        # We provide a fake URL to the enqueue function and expect:
        # - The download PDF function to be called with the URL.
        # - The thumbnails function to be called with the downloaded PDF content and the specified range.
        # - The queue's enqueue function to be called with the expected arguments for adding a status.
        fake_path = faker.url()
        enqueue_posts_for_new_case(self.subscription_w_link, fake_path)

        mock_download_pdf.assert_called_once_with(fake_path)
        mock_thumbnails.assert_called_with(document, "[1,2,3,4]")
        mock_queue.enqueue.assert_called_with(
            api_wrapper.add_status,
            message,
            None,
            [thumb_1, thumb_2],
            retry=mock_retry(),
        )

    @patch("bc.subscription.tasks.add_sponsored_text_to_thumbnails")
    @patch("bc.subscription.tasks.get_thumbnails_from_range")
    @patch("bc.subscription.tasks.download_pdf_from_cl")
    def test_can_create_post_w_sponsored_thumbnails(
        self,
        mock_download_pdf,
        mock_thumbnails,
        mock_sponsored,
        mock_api,
        mock_queue,
        mock_retry,
        mock_docket_by_cl_id,
        mock_lookup,
    ):
        sponsorship = SponsorshipFactory()
        channel_group = GroupFactory(sponsorships=[sponsorship])
        channel = ChannelFactory(mastodon=True, group=channel_group)
        self.subscription_w_link.channel.add(channel)

        api_wrapper = self.mock_api_wrapper()
        mock_api.return_value = api_wrapper

        mock_lookup.return_value = None
        mock_docket_by_cl_id.return_value = None

        fake_path = faker.url()
        document = faker.binary(2)
        mock_download_pdf.return_value = document

        thumb_1 = faker.binary(4)
        thumb_2 = faker.binary(6)
        mock_thumbnails.return_value = [thumb_1, thumb_2]

        thumb_3 = faker.binary(5)
        thumb_4 = faker.binary(7)
        mock_sponsored.return_value = [thumb_3, thumb_4]

        bluesky_message, _ = BLUESKY_FOLLOW_A_NEW_CASE.format(
            docket=self.subscription_w_link.name_with_summary,
            docket_link=self.subscription_w_link.cl_url,
            docket_id=self.subscription_w_link.cl_docket_id,
            article_url=self.subscription_w_link.article_url,
        )

        masto_message, _ = MASTODON_FOLLOW_A_NEW_CASE.format(
            docket=self.subscription_w_link.name_with_summary,
            docket_link=self.subscription_w_link.cl_url,
            docket_id=self.subscription_w_link.cl_docket_id,
            article_url=self.subscription_w_link.article_url,
        )

        enqueue_posts_for_new_case(self.subscription_w_link, fake_path, True)

        expected_enqueue_calls = [
            call(
                api_wrapper.add_status,
                bluesky_message,
                None,
                [thumb_1, thumb_2],
                retry=mock_retry(),
            ),
            call(
                api_wrapper.add_status,
                masto_message,
                None,
                [thumb_3, thumb_4],
                retry=mock_retry(),
            ),
        ]
        mock_download_pdf.assert_called_once_with(fake_path)
        mock_thumbnails.assert_called_once_with(document, "[1,2,3,4]")
        mock_sponsored.assert_called_with(
            [thumb_1, thumb_2], sponsorship.watermark_message
        )
        mock_queue.enqueue.assert_has_calls(
            expected_enqueue_calls, any_order=True
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
        cls.channel = ChannelFactory(bluesky=True)
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
