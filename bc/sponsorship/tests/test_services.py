from decimal import Decimal

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings

from bc.channel.selectors import get_sponsored_groups_per_subscription
from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.sponsorship.models import Transaction
from bc.sponsorship.services import log_purchase
from bc.subscription.tests.factories import (
    FilingWebhookEventFactory,
    SubscriptionFactory,
)
from bc.subscription.types import Document
from bc.users.tests.factories import UserFactory

from .factories import SponsorshipFactory


class LogPurchaseTest(TestCase):
    subscription = None
    webhook_event = None
    act_sponsorship_1 = None
    act_sponsorship_2 = None
    act_sponsorship_3 = None
    group_1 = None
    group_2 = None
    channel_1 = None
    channel_2 = None
    document = None

    @classmethod
    def setUpTestData(cls) -> None:
        cache.clear()
        cls.act_sponsorship_1 = SponsorshipFactory.create_batch(2)
        cls.act_sponsorship_2 = SponsorshipFactory()
        cls.act_sponsorship_3 = SponsorshipFactory()

        cls.group_1 = GroupFactory(sponsorships=cls.act_sponsorship_1)
        cls.group_2 = GroupFactory(sponsorships=[cls.act_sponsorship_2])
        group_3 = GroupFactory(
            sponsorships=[cls.act_sponsorship_2, cls.act_sponsorship_3]
        )
        group_4 = GroupFactory()

        cls.channel_1 = ChannelFactory(group=cls.group_1)
        cls.channel_2 = ChannelFactory(group=cls.group_2)
        channel_3 = ChannelFactory(group=group_3)
        channel_4 = ChannelFactory(group=group_4)

        cls.subscription = SubscriptionFactory(
            channels=[cls.channel_1, cls.channel_2, channel_3, channel_4]
        )
        cls.webhook_event = FilingWebhookEventFactory(
            subscription=cls.subscription,
            docket_id=cls.subscription.cl_docket_id,
        )

        cls.document = Document(
            description=str(cls.webhook_event),
            docket_number=cls.webhook_event.subscription.docket_number,
            court_name=cls.webhook_event.subscription.court_name,
            court_id=cls.webhook_event.subscription.pacer_court_id,
            page_count=10,
        )

    def tearDown(self) -> None:
        cache.clear()
        return super().tearDown()

    def test_can_split_transactions(self):
        sponsored_groups = get_sponsored_groups_per_subscription(
            self.subscription.pk
        )

        log_purchase(
            sponsored_groups, self.webhook_event.subscription.id, self.document
        )

        purchase_transactions = Transaction.objects.filter(
            type=Transaction.DOCUMENT_PURCHASE
        ).all()
        self.assertEqual(purchase_transactions.count(), 2)

    def test_can_log_purchase_after_one_sponsorship_run_out_of_money(self):
        # We need to disable sponsorship 2 to avoid creating a purchase transaction from group 2
        self.act_sponsorship_2.current_amount = 0
        self.act_sponsorship_2.save()

        # We need to disable sponsorship 3 to avoid creating a purchase transaction from group 3
        self.act_sponsorship_3.current_amount = 0
        self.act_sponsorship_3.save()

        sponsored_groups = get_sponsored_groups_per_subscription(
            self.subscription.pk
        )
        log_purchase(
            sponsored_groups, self.webhook_event.subscription.id, self.document
        )

        purchase_transactions = Transaction.objects.filter(
            type=Transaction.DOCUMENT_PURCHASE
        ).all()
        # We should get just one transaction from group 1
        self.assertEqual(purchase_transactions.count(), 1)

    def test_transaction_updates_sponsorship_current_amount(self):
        sponsored_groups = get_sponsored_groups_per_subscription(
            self.subscription.pk
        )
        with self.captureOnCommitCallbacks(execute=True):
            log_purchase(
                sponsored_groups,
                self.webhook_event.subscription.id,
                self.document,
            )

        # Refresh data of active sponsorships
        sponsorship_1 = self.act_sponsorship_1[0]
        sponsorship_1.refresh_from_db()
        self.act_sponsorship_2.refresh_from_db()

        # the document has 10 pages and the log_purchase method evenly
        # divides the total cost among active sponsorships, deducting
        # $.33 from sponsorship record #1 and $.66 from record #2
        self.assertEqual(
            sponsorship_1.current_amount,
            round(sponsorship_1.original_amount - Decimal(1 / 3), 2),
        )
        self.assertEqual(
            self.act_sponsorship_2.current_amount,
            round(self.act_sponsorship_2.original_amount - Decimal(2 / 3), 2),
        )

    @override_settings(LOW_FUNDING_EMAIL_THRESHOLDS=[60.00, 30.00, 3.00])
    def test_can_send_low_fund_emails(self):
        # Create two curators for channel 1
        UserFactory.create_batch(2, channels=[self.channel_1])

        # Update the current amount of the sponsorships for group 1
        for sponsorship in self.act_sponsorship_1:
            sponsorship.current_amount = Decimal(60.00)
            sponsorship.save()

        # Create one curator for channel 2
        UserFactory(channels=[self.channel_2])

        sponsored_groups = get_sponsored_groups_per_subscription(
            self.subscription.pk
        )
        # Adds transaction for sponsorship #1 and #2. Only sponsorship #1
        # will trigger logic to send the first alert
        with self.captureOnCommitCallbacks(execute=True):
            log_purchase(
                sponsored_groups,
                self.webhook_event.subscription.id,
                self.document,
            )

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.group_1.name, mail.outbox[0].body)
        self.assertIn("[Action Needed]:", mail.outbox[0].subject)

        # reload a model’s values from the database
        for sponsorship in self.act_sponsorship_1:
            sponsorship.refresh_from_db()

        self.act_sponsorship_2.current_amount = Decimal(30.00)
        self.act_sponsorship_2.save()

        # Adds another transaction for sponsorship #1 and #2. Sponsorship #2
        # will trigger an alert this time. The logic should skip email for
        # sponsorship #1 because the current amount is bigger than the second
        # threshold.
        with self.captureOnCommitCallbacks(execute=True):
            log_purchase(
                sponsored_groups,
                self.webhook_event.subscription.id,
                self.document,
            )

        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(self.group_2.name, mail.outbox[1].body)
        self.assertIn("[Action Needed, 2nd Notice]:", mail.outbox[1].subject)

        # reload a model’s values from the database
        for sponsorship in self.act_sponsorship_1:
            sponsorship.refresh_from_db()
        self.act_sponsorship_2.refresh_from_db()

        # Adds another transaction for sponsorship #1 and #2. This new
        # transaction should not trigger alerts.
        with self.captureOnCommitCallbacks(execute=True):
            log_purchase(
                sponsored_groups,
                self.webhook_event.subscription.id,
                self.document,
            )

        self.assertEqual(len(mail.outbox), 2)

    @override_settings(LOW_FUNDING_EMAIL_THRESHOLDS=[60.00, 30.00, 3.00])
    def test_add_info_mail_to_final_notice_alert(self):
        # Create two curators for channel 1
        UserFactory.create_batch(2, channels=[self.channel_1])

        # Update the current amount of the sponsorship for group 1
        sponsorship = self.act_sponsorship_1[0]
        sponsorship.current_amount = Decimal(3.10)
        sponsorship.save()

        sponsored_groups = get_sponsored_groups_per_subscription(
            self.subscription.pk
        )
        # Adds transaction for sponsorship #1 and #2. Only sponsorship #1
        # will trigger logic to send the first alert
        with self.captureOnCommitCallbacks(execute=True):
            log_purchase(
                sponsored_groups,
                self.webhook_event.subscription.id,
                self.document,
            )

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.group_1.name, mail.outbox[0].body)
        self.assertIn("[Action Needed, Final Notice]:", mail.outbox[0].subject)
        # check the number of email address in the “Bcc” header
        self.assertEqual(3, len(mail.outbox[0].bcc))
        self.assertIn("info@free.law", mail.outbox[0].bcc)
