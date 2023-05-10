from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from bc.channel.models import Channel, Group


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group


class ChannelFactory(DjangoModelFactory):
    class Meta:
        model = Channel

    service = FuzzyChoice(Channel.CHANNELS, getter=lambda c: c[0])
    group = SubFactory(GroupFactory)
