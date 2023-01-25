from courts_db import find_court_by_id
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from bc.cases.models import Subscription


def view_docket(request: HttpRequest, docket_id: int) -> HttpResponse:
    docket = get_object_or_404(Subscription, pk=docket_id)

    court_name = None
    court_results = find_court_by_id(docket.court)
    if len(court_results) == 1:
        court_name = court_results[0]["name"]

    context = {
        "docket": docket,
        "court_name": court_name,
    }
    return TemplateResponse(request, "docket.html", context)


def count_dockets(request: HttpRequest) -> HttpResponse:
    dockets = Subscription.objects.count()

    context = {"dockets_count": dockets}

    return TemplateResponse(request, "homepage.html", context)
