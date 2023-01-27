import logging

import click
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

from django.conf import settings

from bc.subscription.services import docket_to_case
from bc.subscription.utils.courtlistener import lookup_docket_by_cl_id
from bc.channel.models import Channel


class Command(BaseCommand):
    help = "Add some minimal information for development"

    def handle(self, *args, **options):
        docket = lookup_docket_by_cl_id(65748821)
        case = docket_to_case(docket)

        beat = Beat.objects.create(name="FTX")
        beat.docket.add(case)

        ch = Channel.objects.create(
            service="mastodon",
            account=settings.MASTODON_ACCOUNT,
            account_id=settings.MASTODON_EMAIL,
            enabled=True,
        )

        beat.channels.add(ch)
        
        click.echo(f"Case: {case}")
        click.echo(f"Channel: {ch}")
