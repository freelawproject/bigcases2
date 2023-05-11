from django.conf import settings
from django.db.models import Prefetch, QuerySet

from .models import Channel, Group


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


def get_all_enabled_channels() -> QuerySet[Channel]:
    """
    Returns the set of all enabled channels.

    Returns:
        QuerySet[Channel]: Set of channels
    """
    return Channel.objects.filter(enabled=True).all()


def get_channels_per_subscription(subscription_pk: int) -> QuerySet[Channel]:
    """
    Returns the set of all enabled channels linked to a subscription

    Returns:
        QuerySet[Channel]: Set of channels
    """
    return Channel.objects.filter(
        enabled=True, subscriptions__in=[subscription_pk]
    ).all()


def get_channel_groups_per_user(user_pk: int) -> QuerySet[Group]:
    """
    Returns the list of groups that contains channels related to a user.

    Args:
        user_pk (int): the pk of the user record

    Returns:
        QuerySet[Channel]: Set of groups
    """
    return (
        Group.objects.filter(  # filter the list of groups
            channels__user__in=[user_pk]
        )
        .distinct("id")
        .prefetch_related(
            Prefetch(  # retrieve only channels related to the active user
                "channels", queryset=Channel.objects.filter(user__in=[user_pk])
            )
        )
        .all()
    )
