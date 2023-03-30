from .models import Sponsorship


def get_active_sponsorship() -> Sponsorship | None:
    return (
        Sponsorship.objects.filter(current_amount__gte=3.00)
        .order_by("date_created")
        .first()
    )
