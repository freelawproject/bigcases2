from django.core.management.base import CommandParser

from bc.core.management.commands.command_utils import VerboseCommand
from bc.core.management.commands.make_dev_data import MakeDevData


class Command(VerboseCommand):
    """
    A command for creating dummy data in the system.
    Parses arguments and then sends them to the class to actually make the
    data.
    """

    help = (
        "Create dummy data in your system for development purposes. Uses "
        "Factories. Note: This ADDS to whatever is already in the db."
        "  It doesn't check to see if models (data) already exist."
    )

    DEFAULT_BIG_CASES = 10
    DEFAULT_LITTLE_CASES = 3

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--big-cases",
            "-b",
            type=int,
            default=self.DEFAULT_BIG_CASES,
            help=f"The number of subscriptions to create that will be "
            f"subscribed to the big cases group."
            f"  (integer) Default = {self.DEFAULT_BIG_CASES}",
        )
        parser.add_argument(
            "--little-cases",
            "-l",
            type=int,
            default=self.DEFAULT_LITTLE_CASES,
            help=f"The number of subscriptions to create that will be "
            f"subscribed to the little cases group."
            f"  (integer) Default = {self.DEFAULT_LITTLE_CASES}",
        )
        parser.add_argument(
            "--real-case",
            "-r",
            type=int,
            action="append",
            help=f"Create a subscription with data from a "
            f"real case in Court Listener with the "
            f"Court Listener docket id (integer) that you provide."
            f"  This will be subscribed as a big case.  "
            f"You can use this option multiple times to  subscribe to "
            f"multiple cases. Ex: --real-case 67490069 --real-case 67490070",
        )

    def handle(self, *args, **options) -> None:
        self.requires_migrations_checks = True
        super().handle(*args, **options)

        real_cases = None
        if options["real_case"]:
            real_cases = options["real_case"]

        self._show_and_log("Creating dummy data.... ")
        maker = MakeDevData(
            options["big_cases"],
            options["little_cases"],
            real_cases,
        )
        result_summary = maker.create()
        self._show_and_log(result_summary)
        self._show_and_log("Done.")

    def _show_and_log(self, info_str: str = "") -> None:
        if len(info_str) > 0:
            self.logger.info(info_str)
            print(info_str)
