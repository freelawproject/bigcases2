from typing import Iterable

from django.conf import settings

from .models import Subscription


def get_subscription_by_case_id(case_id) -> Subscription:
    return Subscription.objects.filter(pacer_case_id=case_id).first()
