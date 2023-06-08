from django.test import TestCase

from bc.channel.selectors import get_sponsored_groups_per_subscription
from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.sponsorship.models import Transaction
from bc.sponsorship.services import log_purchase
from bc.subscription.tests.factories import (
    FilingWebhookEventFactory,
    SubscriptionFactory,
)

from .factories import SponsorshipFactory


class LogPurchaseTest(TestCase):
    subscription = None
    webhook_event = None

    @classmethod
    def setUpTestData(cls) -> None:
        act_sponsorship_1 = SponsorshipFactory.create_batch(2)
        act_sponsorship_2 = SponsorshipFactory()
        act_sponsorship_3 = SponsorshipFactory()

        group_1 = GroupFactory(sponsorships=act_sponsorship_1)
        group_2 = GroupFactory(sponsorships=[act_sponsorship_2])
        group_3 = GroupFactory(
            sponsorships=[act_sponsorship_2, act_sponsorship_3]
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

    def test_can_split_transactions(self):
        sponsored_groups = get_sponsored_groups_per_subscription(
            self.subscription.pk
        )
        log_purchase(sponsored_groups, self.webhook_event, 10)

        purchase_transactions = Transaction.objects.filter(
            type=Transaction.DOCUMENT_PURCHASE
        ).all()
        self.assertEqual(purchase_transactions.count(), 2)
