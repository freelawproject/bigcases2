from django.conf import settings
from django.core.management.base import BaseCommand
from mastodon import MastodonNotFoundError

from bc.channel.models import Channel
from bc.channel.utils.connectors.masto import MastodonConnector


class Command(BaseCommand):
    help = "Subscribe to Mastodon mention push notifications."

    def handle(self, *args, **options):
        m = MastodonConnector()
        # Check if there's a subscription already
        try:
            sub = m.push_subscription()
            self.stdout.write(
                self.style.SUCCESS(f"Got an existing subscription: {sub}")
            )
        except MastodonNotFoundError:
            sub = m.subscribe()

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

        Channel.objects.get_or_create(
            account=settings.MASTODON_ACCOUNT,
            account_id=settings.MASTODON_EMAIL,
            defaults={
                "service": Channel.MASTODON,
                "enabled": True,
            },
        )
