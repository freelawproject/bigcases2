from django.db.models import Prefetch, QuerySet

from bc.channel.models import Group

from .models import Sponsorship


def get_sponsorships_for_subscription(
    ids: list[int], subscription_pk: int
) -> QuerySet[Sponsorship]:
    """
    Returns the set of active sponsorships linked to the given subscriptions. This
    method also retrieves, in a single batch, the related groups and uses the Prefetch
    object to further control the operation by providing a custom queryset that filter
    the list of groups.

    Args:
        ids (list[int]): list with the ids of the sponsorship records.
        subscription_pk (int): The pk of the subscription record.

    Returns:
        QuerySet[Sponsorship]: Set of active subscriptions.
    """
    return (
        Sponsorship.objects.filter(id__in=ids)
        .prefetch_related(
            Prefetch(  # retrieve only Groups related to the subscription
                "groups",
                queryset=Group.objects.filter(
                    channels__subscriptions__in=[subscription_pk]
                ).distinct("id"),
            )
        )
        .distinct("id")
        .all()
    )


def check_active_sponsorships(subscription_pk: int) -> int:
    """
    Returns the number of active sponsorships linked to a subscription.

    Args:
        subscription_pk(int): the pk of the subscription record.

    Returns:
        int: number of active sponsorships.
    """
    return (
        Sponsorship.objects.filter(current_amount__gte=3.00)
        .filter(groups__channels__subscriptions__in=[subscription_pk])
        .distinct("id")
        .count()
    )


def get_current_sponsor_organization() -> QuerySet[Sponsorship]:
    """
    Returns the set of active sponsorships.

    Returns:
        QuerySet[Sponsorship]: Set of active sponsorships.
    """
    return (
        Sponsorship.objects.filter(current_amount__gte=3.00)
        .distinct("user_id")
        .all()
    )


def get_past_sponsor_organization() -> QuerySet[Sponsorship]:
    """
    Returns the set of old sponsorships.

    Returns:
        QuerySet[Sponsorship]: Set of old sponsorships.
    """
    return (
        Sponsorship.objects.filter(current_amount__lte=3.00)
        .distinct("user_id")
        .all()
    )
