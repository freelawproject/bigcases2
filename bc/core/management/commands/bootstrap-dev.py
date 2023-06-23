import logging

from django.core.management.base import BaseCommand

from bc.subscription.models import Subscription

logger = logging.getLogger(__name__)

from django.conf import settings

from bc.channel.models import Channel, Group
from bc.subscription.services import create_or_update_subscription_from_docket
from bc.subscription.utils.courtlistener import lookup_docket_by_cl_id


class Command(BaseCommand):
    help = "Add some minimal information for development"

    def handle(self, *args, **options):
        for cl_id in [65748821, 64983976, 66624578]:
            docket: str = lookup_docket_by_cl_id(cl_id)
            subscription, _ = create_or_update_subscription_from_docket(docket)
            self.stdout.write(
                self.style.SUCCESS(f"Subscription: {subscription}")
            )

        ch_group = Group.objects.create(
            name='Big cases',
            is_big_cases=True,
            overview='Group for all big cases',
            slug='big_cases'
        )
        self.stdout.write(
            self.style.SUCCESS(f"Channel Group: {ch_group}")
        )

        mastodon_bigcases_ch = Channel.objects.create(
            service=Channel.MASTODON,
            account=settings.MASTODON_ACCOUNT,
            account_id=settings.MASTODON_EMAIL,
            enabled=True,
            group=ch_group
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Channel: service: {mastodon_bigcases_ch.CHANNELS[mastodon_bigcases_ch.service - 1][1]} account: '{mastodon_bigcases_ch.account}' group: '{mastodon_bigcases_ch.group.name}' enabled? {mastodon_bigcases_ch.enabled}"
            )
        )

        for cl_id in [65748821, 64983976]:
            subscription = Subscription.objects.get(cl_docket_id=cl_id)
            subscription.channel.add(mastodon_bigcases_ch)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Subscription {subscription} was added to the big cases channel."
                )
            )
