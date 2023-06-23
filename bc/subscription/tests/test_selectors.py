from django.test import TestCase

from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.subscription.selectors import get_subscriptions_for_big_cases

from .factories import SubscriptionFactory


class GetSubscriptionsForBigCasesTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        group = GroupFactory(big_cases=True)
        big_cases_channel = ChannelFactory(group=group)

        SubscriptionFactory.create_batch(3)
        SubscriptionFactory.create_batch(2, channels=[big_cases_channel])

    def test_can_list_big_cases_subscriptions(self):
        big_cases_subscriptions = get_subscriptions_for_big_cases()
        self.assertEqual(big_cases_subscriptions.count(), 2)
