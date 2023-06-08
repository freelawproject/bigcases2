from django.test import TestCase

from bc.channel.selectors import get_sponsored_groups_per_subscription
from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.sponsorship.selectors import (
    check_active_sponsorships,
    get_current_sponsor_organization,
    get_past_sponsor_organization,
    get_sponsorships_for_subscription,
)
from bc.subscription.tests.factories import SubscriptionFactory

from .factories import SponsorshipFactory


class GetSponsorshipsForSubscription(TestCase):
    subscription = None

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

    def test_can_get_sponsorships_for_subscription(self):
        groups = get_sponsored_groups_per_subscription(self.subscription.pk)
        self.assertEqual(groups.count(), 3)

        sponsorship_ids = [group.sponsorships.first().pk for group in groups]
        sponsorships = get_sponsorships_for_subscription(
            sponsorship_ids, self.subscription.pk
        )

        self.assertEqual(sponsorships.count(), 2)


class CheckActiveSponsorships(TestCase):
    subscription = None

    @classmethod
    def setUpTestData(cls) -> None:
        past_sponsorships = SponsorshipFactory.create_batch(3)
        for sponsorship in past_sponsorships:
            sponsorship.current_amount = 1.0
            sponsorship.save()

        act_sponsorship_1 = SponsorshipFactory()
        act_sponsorship_2 = SponsorshipFactory()

        group_1 = GroupFactory(
            sponsorships=[act_sponsorship_1] + past_sponsorships
        )
        group_2 = GroupFactory(sponsorships=[act_sponsorship_2])

        channel_1 = ChannelFactory(group=group_1)
        channel_2 = ChannelFactory(group=group_2)

        cls.subscription = SubscriptionFactory(channels=[channel_1, channel_2])

    def test_can_get_number_of_active_subscriptions(self):
        active_count = check_active_sponsorships(self.subscription.pk)
        self.assertEqual(active_count, 2)


class GetListSponsorOrganization(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Create disable sponsorships
        past_sponsorships = SponsorshipFactory.create_batch(4)
        for sponsorship in past_sponsorships:
            sponsorship.current_amount = 1.0
            sponsorship.save()

        # Create a few active sponsorships
        SponsorshipFactory.create_batch(2)

    def test_can_get_list_of_past_sponsorships(self):
        sponsorships = get_past_sponsor_organization()
        self.assertEqual(sponsorships.count(), 4)

    def test_can_get_list_of_current_sponsorships(self):
        sponsorships = get_current_sponsor_organization()
        self.assertEqual(sponsorships.count(), 2)
