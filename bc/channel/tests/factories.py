import factory
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from bc.channel.models import Channel, Group


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    @factory.post_generation
    def sponsorships(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.sponsorships.add(*extracted)


class ChannelFactory(DjangoModelFactory):
    class Meta:
        model = Channel

    service = FuzzyChoice(Channel.CHANNELS, getter=lambda c: c[0])
    group = SubFactory(GroupFactory)
