import factory
from factory import SubFactory
from factory.django import DjangoModelFactory

from bc.core.utils.tests.base import faker
from bc.sponsorship.models import Sponsorship, Transaction
from bc.users.tests.factories import UserFactory


class SponsorshipFactory(DjangoModelFactory):
    class Meta:
        model = Sponsorship

    original_amount = factory.LazyAttribute(
        lambda _: faker.random_number(digits=3, fix_len=True)
    )
    user = SubFactory(UserFactory)


class TransactionFactory(DjangoModelFactory):
    """
    Traits:
      - purchase: Create a transaction for a document purchase
    """

    class Meta:
        model = Transaction

    user = SubFactory(UserFactory)
    sponsorship = SubFactory(SponsorshipFactory)
    amount = factory.LazyAttribute(
        lambda _: faker.random_number(digits=2, fix_len=True)
    )

    class Params:
        purchase = factory.Trait(
            type=Transaction.DOCUMENT_PURCHASE, note="fake Document purchase"
        )
