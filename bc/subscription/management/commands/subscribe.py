from django.core.management.base import BaseCommand

from bc.channel.models import Channel, Group
from bc.core.utils.commands import (
    show_all_channels_table,
    show_channel_groups_table,
)
from bc.subscription.models import Subscription
from bc.subscription.services import create_or_update_subscription_from_docket
from bc.subscription.tasks import enqueue_posts_for_new_case
from bc.subscription.utils.courtlistener import (
    lookup_docket_by_cl_id,
    subscribe_to_docket_alert,
)


def link_channels_to_subscription(
    ids: list[int],
    mapping: dict[int, Channel | Group],
    subscription: Subscription,
):
    """
    Takes the mapping from the command and creates a link between the subscription
    and the channel.

    Args:
        ids (list[int]): list of the id from the user's input
        mapping (dict[int, Channel  |  Group]): Mapping of objects in the table
        subscription (Subscription): The subscription object.

    Raises:
        ValueError: if the provided input is not in the mapping variable.
    """
    for record_id in ids:
        record = mapping.get(record_id)

        if record is None:
            raise ValueError(f"No channel {record_id}")

        if isinstance(record, Group):
            for channel in record.channels.all():
                subscription.channel.add(channel)
        else:
            subscription.channel.add(record)


class Command(BaseCommand):
    help = (
        "Lookup a case in the RECAP archive by its CourtListener ID and "
        "add it to the db."
    )

    def add_arguments(self, parser):
        parser.add_argument("cl-id", type=str)
        parser.add_argument(
            "--show_groups",
            action="store_true",
            help="Shows the list of groups instead of individual channels",
        )

    def handle(self, *args, **options):
        result = lookup_docket_by_cl_id(options["cl-id"])
        if not result:
            self.stdout.write(self.style.ERROR("Case not found"))
            return

        court = result["court_id"]
        case_name = result["case_name"]
        docket_number = result["docket_number"]
        uri = result["absolute_url"]
        cl_url = f"https://www.courtlistener.com{uri}"
        self.stdout.write(self.style.SUCCESS(f"Name: {case_name}"))
        self.stdout.write(self.style.SUCCESS(f"Case no.: {docket_number}"))
        self.stdout.write(self.style.SUCCESS(f"Court: {court}"))
        self.stdout.write(self.style.SUCCESS(f"Link: {cl_url}"))

        name = result["case_name"]
        custom_name = input(
            "\nEnter a name for this case or press enter to use the default:\n\n"
            f"Default: {name}\n"
            "name: "
        )
        if custom_name:
            result["case_name"] = custom_name or name
            self.stdout.write(
                self.style.WARNING(
                    f"We'll rename the case to: '{custom_name}'."
                )
            )

        case_summary = input(
            "\nEnter a summary for this case or press enter to leave it empty:\n\n"
            "summary: "
        )
        if case_summary:
            result["case_summary"] = case_summary

        instance = "group" if options["show_groups"] else "channel"
        self.stdout.write(
            self.style.SUCCESS(
                f"\nPick one of more {instance}s from the following table to link to this subscription"
            )
        )

        if options["show_groups"]:
            table, mapping = show_channel_groups_table()
        else:
            table, mapping = show_all_channels_table()

        self.stdout.write(self.style.SUCCESS(table))

        ch_input = input(
            f"Which {instance}? Input ID, comma-separate for multiple, "
            "or 'all' for all of them.\n"
        )

        if ch_input == "all":
            input_ids = list(mapping.keys())
        else:
            input_ids = list(
                map(int, [s.strip() for s in ch_input.split(",")])
            )

        self.stdout.write(
            self.style.WARNING("We'll try to add this case to the DB.")
        )

        subscription, created = create_or_update_subscription_from_docket(
            result
        )

        link_channels_to_subscription(input_ids, mapping, subscription)

        message = "Added!" if created else "Updated!"
        self.stdout.write(self.style.SUCCESS(message))

        if not created:
            return

        cl_subscription = subscribe_to_docket_alert(options["cl-id"])
        if cl_subscription:
            self.stdout.write(self.style.SUCCESS("Subscribed!"))

        enqueue_posts_for_new_case(subscription)
