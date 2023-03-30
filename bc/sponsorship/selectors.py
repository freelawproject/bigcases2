from .models import Sponsorship


def get_available_sponsorship() -> Sponsorship | None:
    return Sponsorship.objects.filter(current_amount__gte=3.00).first()
