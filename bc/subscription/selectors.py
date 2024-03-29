from django.db.models import QuerySet

from .models import Subscription


def get_subscription_by_case_id(case_id) -> Subscription | None:
    return Subscription.objects.filter(pacer_case_id=case_id).first()


def get_subscriptions_for_big_cases() -> QuerySet[Subscription]:
    """
    Returns the list of subscriptions for the Big Cases bot.

    Returns:
        QuerySet[Subscription]: list of subscriptions
    """
    return (
        Subscription.objects.filter(channel__group__is_big_cases=True)
        .distinct("cl_docket_id")
        .all()
    )
