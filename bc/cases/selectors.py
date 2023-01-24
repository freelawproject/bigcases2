from typing import Iterable

from django.conf import settings

from .models import Docket


def get_docket_by_case_number(docket_number, court_key) -> Docket:
    return Docket.objects.filter(
        docket_number=docket_number, court=court_key
    ).first()


def get_dockets_from_bcb1() -> Iterable[Docket]:
    return Docket.objects.filter(
        in_bcb1=True, cl_docket_id__isnull=True
    ).all()[: settings.BCB_MATCH_LIMIT]
