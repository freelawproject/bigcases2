from typing import Optional

from .models import Subscription


def get_subscription_by_case_id(case_id) -> Optional[Subscription]:
    return Subscription.objects.filter(pacer_case_id=case_id).first()
