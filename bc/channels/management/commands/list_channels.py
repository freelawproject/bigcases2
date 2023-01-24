import click
from django.core.management.base import BaseCommand
from prettytable import PrettyTable

from bc.channels.models import Channel


class Command(BaseCommand):
    help = "List channels to which BCB2 can post."

    def handle(self, *args, **options):
        tab = PrettyTable()
        db_channels = Channel.objects.all()
        click.echo(db_channels)

        channel_mapping = {}
        tab.field_names = ["ID", "Service", "Account", "Enabled", "URL"]
        db_channels = Channel.objects.all()
        for channel in db_channels:
            tab.add_row(
                [
                    channel.id,
                    channel.service,
                    channel.account,
                    channel.enabled,
                    channel.self_url(),
                ]
            )
            channel_mapping[channel.id] = channel
        click.echo(tab)
