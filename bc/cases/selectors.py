from typing import Iterable

from django.conf import settings

from .models import Subscription


def get_docket_by_case_number(docket_number, court_key) -> Subscription:
    return Subscription.objects.filter(
        docket_number=docket_number, court=court_key
    ).first()
