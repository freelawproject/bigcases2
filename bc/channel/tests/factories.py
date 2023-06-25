import factory
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from bc.channel.models import Channel, Group
from bc.core.utils.tests.base import faker


def fake_token(format_str: str = "#############") -> str:
    """
    Return a string filled with random letters and numbers that can be used
    to fake a token. The string is based on the format_str provided.

    Args:
        format_str (str): format string that faker.pystr_format will use.
          Default is "#############" (13 characters ('#') long).

    Returns:
        (str): A string filled with random letters and numbers

    """
    return faker.pystr_format(f"{format_str}{{{{random_letter}}}}")


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    @factory.post_generation
    def sponsorships(self, create, extracted, **_kwargs):
        if not create or not extracted:
            return

        self.sponsorships.add(*extracted)


class ChannelFactory(DjangoModelFactory):
    class Meta:
        model = Channel

    service = FuzzyChoice(Channel.CHANNELS, getter=lambda c: c[0])
    group = SubFactory(GroupFactory)
    access_token = factory.LazyAttribute(lambda _: fake_token())
    access_token_secret = factory.LazyAttribute(
        lambda _: fake_token("####################")
    )
