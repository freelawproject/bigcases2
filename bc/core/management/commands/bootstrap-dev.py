import logging

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

from django.conf import settings

from bc.channel.models import Channel
from bc.subscription.services import create_subscription_from_docket
from bc.subscription.utils.courtlistener import lookup_docket_by_cl_id


class Command(BaseCommand):
    help = "Add some minimal information for development"

    def handle(self, *args, **options):
        for cl_id in [65748821, 64983976, 66624578]:
            docket = lookup_docket_by_cl_id(cl_id)
            subscription = create_subscription_from_docket(docket)
            self.stdout.write(
                self.style.SUCCESS(f"Subscription: {subscription}")
            )

        ch = Channel.objects.create(
            service="mastodon",
            account=settings.MASTODON_ACCOUNT,
            account_id=settings.MASTODON_EMAIL,
            enabled=True,
        )

        self.stdout.write(self.style.SUCCESS(f"Channel: {ch}"))
