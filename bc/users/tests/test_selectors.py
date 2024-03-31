from django.test import TestCase

from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.users.selectors import get_curators_by_channel_group_id
from bc.users.tests.factories import UserFactory


class GetGroupsWithLowFunding(TestCase):
    group_1 = None
    group_2 = None
    channels_g2 = None

    @classmethod
    def setUpTestData(cls) -> None:
        # Create 2 channel with a sponsorship
        cls.group_1 = GroupFactory()
        cls.group_2 = GroupFactory()

        # Link groups to a few channels
        channels_g1 = ChannelFactory.create_batch(2, group=cls.group_1)
        cls.channels_g2 = ChannelFactory.create_batch(3, group=cls.group_2)

        # Link both channels to user #1
        UserFactory(channels=channels_g1)

        # Link just one channel from group 1 to user #2
        UserFactory(channels=[channels_g1[0]])

    def test_can_get_curators_user_group_id(self):
        # Query curators for group #1
        users = get_curators_by_channel_group_id(self.group_1.pk)
        self.assertEqual(users.count(), 2)

        # Query curators for group #2
        users = get_curators_by_channel_group_id(self.group_2.pk)
        self.assertEqual(users.count(), 0)

        # Adds curators to the channels in group #2
        UserFactory(channels=self.channels_g2)

        # Query curators for group #2 again
        users = get_curators_by_channel_group_id(self.group_2.pk)
        self.assertEqual(users.count(), 1)
