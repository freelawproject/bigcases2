import factory
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

from bc.core.utils.legal_provider import LegalProvider
from bc.core.utils.tests.base import faker
from bc.subscription.models import FilingWebhookEvent, Subscription

local_faker = Faker()
local_faker.add_provider(LegalProvider)


class SubscriptionFactory(DjangoModelFactory):
    class Meta:
        model = Subscription

    cl_docket_id = factory.LazyAttribute(
        lambda _: faker.random_int(100_000, 400_000)
    )
    docket_name = factory.LazyFunction(local_faker.case_name)
    docket_number = factory.LazyFunction(local_faker.docket_number)
    court_name = factory.LazyAttribute(lambda _: local_faker.court_name())

    @factory.post_generation
    def channels(self, create, extracted, **kwargs):
        """
        Add channels to this subscription
        @see https://factoryboy.readthedocs.io/en/stable/reference.html?highlight=post_generation#post-generation-hooks
        @example:
            some_channel = ChannelFactory.create()
            SubscriptionFactory(channels=[channel_1, channel_2]) #
            subscribes this to channel_1 and channel_2
        """
        if not create or not extracted:
            return
        print(f"extracted: {extracted}")
        self.channel.add(*extracted)
        print(f"self.channel: {self.channel}")


class FilingWebhookEventFactory(DjangoModelFactory):
    class Meta:
        model = FilingWebhookEvent

    docket_id = factory.LazyAttribute(
        lambda _: faker.random_int(100_000, 400_000)
    )
    pacer_doc_id = factory.LazyAttribute(
        lambda _: faker.pystr(min_chars=10, max_chars=32)
    )
    long_description = factory.LazyAttribute(
        lambda _: faker.pystr(min_chars=300, max_chars=400)
    )
    short_description = factory.LazyAttribute(
        lambda _: faker.pystr(min_chars=10, max_chars=20)
    )
    subscription = SubFactory(SubscriptionFactory)
