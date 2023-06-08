from faker import Faker
from faker.providers import python

faker = Faker()
faker.add_provider(python)
