from django.test import TestCase

from bc.channel.selectors import (
    get_all_enabled_channels,
    get_channel_groups_per_user,
    get_channels_per_subscription,
    get_groups_with_low_funding,
)
from bc.sponsorship.tests.factories import SponsorshipFactory
from bc.subscription.tests.factories import SubscriptionFactory
from bc.users.tests.factories import UserFactory

from .factories import ChannelFactory, GroupFactory


class GetAllEnabledChannels(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Create a few disabled channels
        ChannelFactory.create_batch(4)

        # Create enabled channels
        ChannelFactory.create_batch(2, enabled=True)

    def test_can_get_list_of_enable_channels(self):
        channels = get_all_enabled_channels()
        self.assertEqual(channels.count(), 2)


class GetChannelsPerSubscription(TestCase):
    subscription = None

    @classmethod
    def setUpTestData(cls) -> None:
        # Create a few active channels
        ChannelFactory.create_batch(4, enabled=True)
        # Channels for the subscription
        channels_for_subscription = ChannelFactory.create_batch(
            10, enabled=True
        )
        cls.subscription = SubscriptionFactory(
            channels=channels_for_subscription
        )

    def test_can_get_enable_channels_linked_to_subscription(self):
        channels = get_channels_per_subscription(self.subscription.pk)
        self.assertEqual(channels.count(), 10)


class GetChannelGroupsPerUser(TestCase):
    user = None

    @classmethod
    def setUpTestData(cls) -> None:
        # create 2 groups of channels
        group_1 = GroupFactory()
        group_2 = GroupFactory()

        # Link groups to a few channels
        channels_g1 = ChannelFactory.create_batch(2, group=group_1)
        channels_g2 = ChannelFactory.create_batch(3, group=group_2)

        # create more groups of channels
        ChannelFactory.create_batch(6)

        # link the first channel from two of the groups to the user object
        cls.user = UserFactory(channels=[channels_g1[0], channels_g2[0]])

    def test_can_get_groups_linked_to_users(self):
        groups = get_channel_groups_per_user(self.user.pk)
        # check the number of groups
        self.assertEqual(groups.count(), 2)
        for group in groups:
            # check the number of channels per group
            self.assertEqual(group.channels.count(), 1)


class GetGroupsWithLowFunding(TestCase):
    group_1 = None
    group_2 = None

    @classmethod
    def setUpTestData(cls) -> None:
        # Create 2 sponsorships and update the current amount
        old_sponsorship_1 = SponsorshipFactory()
        old_sponsorship_1.current_amount = 10.0
        old_sponsorship_1.save()

        old_sponsorship_2 = SponsorshipFactory()
        old_sponsorship_2.current_amount = 20.0
        old_sponsorship_2.save()

        # Create 2 channel with a sponsorship
        cls.group_1 = GroupFactory(sponsorships=[old_sponsorship_1])
        cls.group_2 = GroupFactory(sponsorships=[old_sponsorship_2])

    def test_can_get_groups_with_low_funding(self):
        """Can we get groups with low funding"""
        low_funding_groups = get_groups_with_low_funding()
        self.assertEqual(low_funding_groups.count(), 2)

        # Add a big sponsorship for one of the groups
        sponsorship = SponsorshipFactory(original_amount=400)
        self.group_1.sponsorships.add(sponsorship)

        low_funding_groups = get_groups_with_low_funding()
        self.assertEqual(low_funding_groups.count(), 1)
        self.assertEqual(
            list(low_funding_groups.values_list("id", flat=True)),
            [self.group_2.pk],
        )

    def test_exclude_groups_with_no_sponsorship(self):
        """Can the query exclude groups with no sponsorships"""
        # Create six channels with no sponsorship
        GroupFactory.create_batch(6)

        # Get the list of groups with low funding
        low_funding_groups = get_groups_with_low_funding()
        self.assertEqual(low_funding_groups.count(), 2)
