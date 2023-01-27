from django.conf import settings
from django.core.management.base import BaseCommand

from bc.channel.models import Channel
from bc.channel.utils.masto import get_mastodon


class Command(BaseCommand):
    help = "Delete push subscription."

    def handle(self, *args, **options):
        m = get_mastodon()
        m.push_subscription_delete()
        self.stdout.write(self.style.SUCCESS("Deleted push subscription."))

        existing_channel = Channel.objects.filter(
            account=settings.MASTODON_ACCOUNT,
            account_id=settings.MASTODON_EMAIL,
        ).first()
        if existing_channel:
            existing_channel.delete()
