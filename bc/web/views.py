from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from bc.subscription.models import Subscription

from .forms import BotSuggestionForm, WaitListForm


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


def little_cases(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = BotSuggestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("successful_submission")
    else:
        form = BotSuggestionForm()

    return TemplateResponse(request, "little_cases.html", {"form": form})


def collaboration(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = WaitListForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("successful_submission")
    else:
        form = WaitListForm()

    return TemplateResponse(request, "collaboration.html", {"form": form})
