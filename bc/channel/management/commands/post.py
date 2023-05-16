from django.core.management.base import BaseCommand

from bc.channel.models import Channel, Group
from bc.channel.tasks import (
    enqueue_text_status_for_channel,
    enqueue_text_status_for_group,
)
from bc.core.utils.commands import (
    show_all_channels_table,
    show_channel_groups_table,
)


def handle_post_command(
    ids: list[int], mapping: dict[int, Channel | Group], text: str
) -> None:
    """
    Enqueues a job to create a post for each channel in the list of ids provided
    by the user.

    Args:
        ids (list[int]): list of the id from the user's input.
        mapping (dict[int, Channel  |  Group]): Mapping of objects in the table.
        text (str): Text to include in the posts.

    Raises:
        ValueError: if the provided input is not in the mapping variable.
    """
    for record_id in ids:
        record = mapping.get(record_id)

        if record is None:
            raise ValueError(f"No channel {record_id}")

        if isinstance(record, Group):
            enqueue_text_status_for_group(record, text)
        else:
            enqueue_text_status_for_channel(record, text)


class Command(BaseCommand):
    help = "Post something manually to one or more channels."

    def add_arguments(self, parser):
        parser.add_argument(
            "--show_channels",
            action="store_true",
            help="Shows the list of individual channels",
        )

    def handle(self, *args, **options):
        if not options["show_channels"]:
            table, mapping = show_channel_groups_table()
        else:
            table, mapping = show_all_channels_table()

        self.stdout.write(self.style.SUCCESS(table))

        instance = "channel" if options["show_channels"] else "group"

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

        post_text = input("What do you want to say? ")

        self.stdout.write(
            self.style.SUCCESS(
                f"Here's what we're going to say:\n\t{post_text}"
            )
        )

        handle_post_command(input_ids, mapping, post_text)
