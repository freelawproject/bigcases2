from collections.abc import Iterable

from .models import Sponsorship


def get_active_sponsorship() -> Sponsorship | None:
    return (
        Sponsorship.objects.filter(current_amount__gte=3.00)
        .order_by("date_created")
        .first()
    )


def get_current_sponsor_organization() -> Iterable[Sponsorship]:
    return (
        Sponsorship.objects.filter(current_amount__gte=3.00)
        .distinct("user_id")
        .all()
    )


def get_past_sponsor_organization() -> Iterable[Sponsorship]:
    return (
        Sponsorship.objects.filter(current_amount__lte=3.00)
        .distinct("user_id")
        .all()
    )
