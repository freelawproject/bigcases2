from collections.abc import Iterable

from django.conf import settings

from .models import Channel


def get_mastodon_channel() -> Channel:
    obj, _ = Channel.objects.get_or_create(
        account=settings.MASTODON_ACCOUNT,
        account_id=settings.MASTODON_EMAIL,
        defaults={
            "service": Channel.MASTODON,
            "enabled": True,
        },
    )
    return obj


def get_all_enabled_channels() -> Iterable[Channel]:
    """Returns the set of all enabled channels.

    Returns:
        Iterable[Channel]: Set of channels
    """
    return Channel.objects.filter(enabled=True).all()
