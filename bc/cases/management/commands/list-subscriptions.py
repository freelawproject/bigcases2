from pprint import pformat

import click
from django.core.management.base import BaseCommand

from bc.cases.utils.courtlistener import get_docket_alert_subscriptions


class Command(BaseCommand):
    help = "List CourtListener docket alert subscriptions"

    def handle(self, *args, **options):
        subs = get_docket_alert_subscriptions()
        click.echo("Subscriptions: (CourtListener IDs)")
        click.echo(pformat(subs))
