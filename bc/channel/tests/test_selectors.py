from django.test import TestCase

from bc.channel.selectors import (
    get_all_enabled_channels,
    get_channel_groups_per_user,
    get_channels_per_subscription,
)
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
