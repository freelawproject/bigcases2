# This is based on CourtListener cl/lib/management/make_dev_data.py
# TODO create 1 common library that both (all) FLP can use
from logging import Logger

from django.core.management.base import CommandParser
from faker import Faker

from bc.channel.models import Group
from bc.channel.tests.factories import ChannelFactory, GroupFactory
from bc.core.management.commands.command_utils import logger, VerboseCommand
from bc.subscription.models import Subscription
from bc.subscription.tests.factories import SubscriptionFactory
from bc.users.tests.factories import AdminFactory

fake = Faker()


class Command(VerboseCommand):
    help = "Create dummy data in your system for development purposes. Uses Factories"

    DEFAULT_NUM_CASES = 10

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--num-big-cases",
            type=int,
            default=self.DEFAULT_NUM_CASES,
            help=f"The number of big cases to create. Default = 1",
        )

    def handle(self, *args, **options) -> None:
        requires_migrations_checks = True
        super(Command, self).handle(*args, **options)

        num_big_cases = 1
        if options["num_big_cases"]:
            num_big_cases = options["num_big_cases"]

        logger.info(
            f"Creating dummy data. Making at least {num_big_cases} "
            f"objects of each type."
        )

        maker = MakeDevData(logger, num_big_cases)
        maker.create_from_factories(maker)

        logger.info('Done.')


class MakeDevData:
    """
    Use existing factories to create data.
    Log information to the logger, if given.
    Create the given number of 'big cases'.

    When finished (if successful), logs a readable summary of how many objects were created.
    """

    def __init__(self, logger: Logger | None, num_big_cases=1) -> None:
        self.logger = logger
        self.num_big_cases = num_big_cases

    @staticmethod
    def create_from_factories(self) -> None:
        num_subscriptions = 10
        summary = '\nCreated and saved data. Made:\n'
        try:
            summary += self.make_admin_users(1) + '\n'
            summary += self.make_big_cases_group_and_channels() + '\n'
            summary += self.make_subscriptions(num_subscriptions) + '\n'

            big_cases_bots = Group.objects.filter(is_big_cases=True).all()
            num_to_subscribe = (num_subscriptions * 4) // 10  # about 40%
            summary += self.subscribe_to_big_cases(big_cases_bots,
                                                   num_to_subscribe) + '\n'

            logger.info(summary)
            print(summary)

        except Exception as err:
            logger.error(f"Unexpected {err=}, {type(err)=}")
            raise

    def make_admin_users(self, num=1):
        info = 'Admin user(s)'
        self.log_making(self, num, info)
        AdminFactory.create_batch(num)
        return self.made_str(self, num, info)

    def make_big_cases_group_and_channels(self, num=1):
        info = 'Big Cases Group and the Mastodon and Twitter Channels'
        self.log_making(self, num, info)
        big_cases_group = GroupFactory.create(big_cases=True)
        ChannelFactory.create(mastodon=True, group=big_cases_group)
        ChannelFactory.create(twitter=True, group=big_cases_group)

        return self.made_str(self, num, info)

    def make_subscriptions(self, num=5) -> str:
        """
        Make subscriptions.The first three are hardcoded.
        This is so developers can work with subscriptions they've been used
        to seeing, and so they can always work with some consistent, known
        information.
        All other subscriptions are generated with random info.
        """
        for i in range(0, num):
            SubscriptionFactory.create()
        return self.made_str(self, num, 'Subscriptions')

    def subscribe_to_big_cases(self, big_cases_bots, num=3) -> str:
        """
            Pick {num} random subscriptions and add them to the big_cases channel
        """
        subscription_ids = list(Subscription.objects.all()
                                .values_list('id', flat=True))
        random_subscription_ids = fake.random_elements(subscription_ids,
                                                       length=num, unique=True)
        for sub_id in random_subscription_ids:
            subscription = Subscription.objects.get(id=sub_id)
            for big_case_bot in big_cases_bots:
                for channel in big_case_bot.channels.all():
                    subscription.channel.add(channel)
        return self.made_str(self, num,
                             f'big case subscriptions (Subscription ids = {random_subscription_ids})')

    @staticmethod
    def log_making(self, num: int = 1, info: str = ''):
        if not logger is None:
            logger.info(f">> Making {num} {info}")

    @staticmethod
    def made_str(self, num: int = 1, info: str = '') -> str:
        return f"   {num} {info}"
