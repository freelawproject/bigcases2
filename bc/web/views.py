from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from bc.sponsorship.selectors import (
    get_current_sponsor_organization,
    get_past_sponsor_organization,
)
from bc.subscription.models import Subscription

from .forms import BotSuggestionForm, WaitListForm


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

    return TemplateResponse(request, "little-cases.html", {"form": form})


def collaboration(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = WaitListForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("successful_submission")
    else:
        form = WaitListForm()

    return TemplateResponse(request, "collaboration.html", {"form": form})


def big_cases_about(request: HttpRequest) -> HttpResponse:
    """The BCB about page"""
    return TemplateResponse(
        request,
        "big-cases/about.html",
        {
            "subscriptions": Subscription.objects.all(),
        },
    )


def big_cases_sponsors(request: HttpRequest) -> HttpResponse:
    """The BCB sponsors page"""
    return TemplateResponse(
        request,
        "big-cases/sponsors.html",
        {
            "current_sponsors": get_current_sponsor_organization(),
            "past_sponsors": get_past_sponsor_organization(),
        },
    )


def ratelimited(request: HttpRequest, exception: Exception) -> HttpResponse:
    return TemplateResponse(
        request,
        "429.html",
        status=HTTPStatus.TOO_MANY_REQUESTS,
    )
