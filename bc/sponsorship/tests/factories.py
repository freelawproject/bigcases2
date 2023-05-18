import factory
from factory import SubFactory
from factory.django import DjangoModelFactory

from bc.core.utils.tests.base import faker
from bc.sponsorship.models import Sponsorship
from bc.users.tests.factories import UserFactory


class SponsorshipFactory(DjangoModelFactory):
    class Meta:
        model = Sponsorship

    original_amount = factory.LazyAttribute(
        lambda _: faker.random_number(digits=3, fix_len=True)
    )
    user = SubFactory(UserFactory)
