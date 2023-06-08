import factory
from factory import SubFactory
from factory.django import DjangoModelFactory

from bc.core.utils.tests.base import faker
from bc.subscription.models import FilingWebhookEvent, Subscription


class SubscriptionFactory(DjangoModelFactory):
    class Meta:
        model = Subscription

    cl_docket_id = factory.LazyAttribute(
        lambda _: faker.random_int(100_000, 400_000)
    )

    @factory.post_generation
    def channels(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.channel.add(*extracted)


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
