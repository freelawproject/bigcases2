import click
from django.core.management.base import BaseCommand

from bc.channels.utils.masto import get_mastodon


class Command(BaseCommand):
    help = "Delete push subscription."

    def handle(self, *args, **options):
        m = get_mastodon()
        m.push_subscription_delete()
        click.echo("Deleted push subscription.")
