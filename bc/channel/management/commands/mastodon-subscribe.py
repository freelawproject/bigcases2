from django.conf import settings
from django.core.management.base import BaseCommand
from mastodon import MastodonNotFoundError

from bc.channel.models import Channel
from bc.channel.utils.masto import get_mastodon, subscribe


class Command(BaseCommand):
    help = "Subscribe to Mastodon mention push notifications."

    def handle(self, *args, **options):
        m = get_mastodon()
        # Check if there's a subscription already
        try:
            sub = m.push_subscription()
            self.stdout.write(
                self.style.SUCCESS(f"Got an existing subscription: {sub}")
            )
        except MastodonNotFoundError as e:
            sub = subscribe()

        sub_id = sub["id"]
        sub_key = sub["server_key"]
        self.stdout.write(
            self.style.SUCCESS(
                f"Push subscription ID: {sub_id}. Key: {sub_key}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS("mastodon_subscribe_command() done.")
        )

        existing_channel = Channel.objects.filter(
            account=settings.MASTODON_ACCOUNT,
            account_id=settings.MASTODON_EMAIL,
        ).first()
        if not existing_channel:
            ch = Channel.objects.create(
                service="mastodon",
                account=settings.MASTODON_ACCOUNT,
                account_id=settings.MASTODON_EMAIL,
                enabled=True,
            )
