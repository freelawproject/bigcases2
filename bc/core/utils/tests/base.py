from faker import Faker
from faker.providers import internet, python

faker = Faker()
faker.add_provider(python)
faker.add_provider(internet)
