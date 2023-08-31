from django.test import TestCase

from bc.channel.selectors import get_sponsored_groups_per_subscription
from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.sponsorship.models import Transaction
from bc.sponsorship.services import log_purchase
from bc.subscription.tests.factories import (
    FilingWebhookEventFactory,
    SubscriptionFactory,
)
from bc.subscription.types import Document

from .factories import SponsorshipFactory


class LogPurchaseTest(TestCase):
    subscription = None
    webhook_event = None
    act_sponsorship_2 = None
    act_sponsorship_3 = None
    document = None

    @classmethod
    def setUpTestData(cls) -> None:
        act_sponsorship_1 = SponsorshipFactory.create_batch(2)
        cls.act_sponsorship_2 = SponsorshipFactory()
        cls.act_sponsorship_3 = SponsorshipFactory()

        group_1 = GroupFactory(sponsorships=act_sponsorship_1)
        group_2 = GroupFactory(sponsorships=[cls.act_sponsorship_2])
        group_3 = GroupFactory(
            sponsorships=[cls.act_sponsorship_2, cls.act_sponsorship_3]
        )
        group_4 = GroupFactory()

        channel_1 = ChannelFactory(group=group_1)
        channel_2 = ChannelFactory(group=group_2)
        channel_3 = ChannelFactory(group=group_3)
        channel_4 = ChannelFactory(group=group_4)

        cls.subscription = SubscriptionFactory(
            channels=[channel_1, channel_2, channel_3, channel_4]
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
