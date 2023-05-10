import factory
from django.contrib.auth.hashers import make_password
from factory import LazyAttribute, LazyFunction
from factory.django import DjangoModelFactory

from bc.core.utils.tests.base import faker
from bc.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = LazyAttribute(lambda _: faker.user_name())
    first_name = LazyAttribute(lambda _: faker.first_name())
    last_name = LazyAttribute(lambda _: faker.last_name())
    email = LazyAttribute(lambda _: faker.email())
    password = LazyFunction(lambda: make_password("password"))
    is_staff = False
    is_superuser = False
    is_active = True

    @factory.post_generation
    def channels(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.channels.add(*extracted)
