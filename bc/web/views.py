from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from bc.subscription.models import Subscription


def view_docket(request: HttpRequest, subscription_id: int) -> HttpResponse:
    subscription = get_object_or_404(Subscription, pk=subscription_id)
    return TemplateResponse(
        request, "docket.html", {"subscription": subscription}
    )


def count_dockets(request: HttpRequest) -> HttpResponse:
    subscription_count = Subscription.objects.count()

    return TemplateResponse(
        request, "homepage.html", {"subscription_count": subscription_count}
    )
