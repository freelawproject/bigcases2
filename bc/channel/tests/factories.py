import factory
from django.utils.text import slugify
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
    """
    Traits:
      - big_cases  Create a Group with is_big_cases=True and the name "Big
      cases" and some other attributes
        Ex: `GroupFactory(big_cases=True)`
      - little_cases  Create a Group with is_big_cases=False and the name
      "Little cases" and some other attributes
        Ex: `GroupFactory(big_cases=True)`

    Post-generation:
        After creating, will optionally also create sponsorships using the
        `@factory.post_generation` decorator.
          - Ex: GroupFactory(sponsorships=[<some list of Sponsorships>])
    """

    class Meta:
        model = Group

    name = factory.LazyFunction(faker.last_name)
    is_big_cases = False
    overview = factory.LazyAttribute(lambda obj: f"Group for {obj.name}")
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))

    @factory.post_generation
    def sponsorships(self, create, extracted, **_kwargs):
        if not create or not extracted:
            return

        self.sponsorships.add(*extracted)

    class Params:
        big_cases = factory.Trait(
            name="Big cases",
            is_big_cases=True,
            overview="Group for all big cases",
            slug="big_cases",
        )
        little_cases = factory.Trait(
            name="Little cases",
            overview="Group for all little cases",
            slug="little_cases",
        )


class ChannelFactory(DjangoModelFactory):
    """
    Traits:
      - mastodon Create an enabled Channel for Mastodon
      - twitter Create an enabled Channel for Twitter
    """

    class Meta:
        model = Channel

    enabled = False
    access_token = factory.LazyFunction(fake_token)
    access_token_secret = factory.LazyAttribute(
        lambda _: fake_token("####################")
    )
    service = FuzzyChoice(Channel.CHANNELS, getter=lambda c: c[0])
    group = SubFactory(GroupFactory)

    class Params:
        mastodon = factory.Trait(
            service=Channel.MASTODON,
            account="BigCases2-faux",
            account_id="Mastodon-big-cases-email-faux",
            enabled=True,
        )
        twitter = factory.Trait(
            service=Channel.TWITTER,
            account="BigCases2-faux",
            account_id="Twitter-big-cases-email-faux",
            enabled=True,
        )
