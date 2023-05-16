from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views import View
from django_htmx.http import trigger_client_event
from requests.exceptions import HTTPError
from rest_framework.request import Request
from rest_framework.response import Response

from bc.channel.models import Group
from bc.channel.selectors import get_channel_groups_per_user

from .services import create_or_update_subscription_from_docket
from .tasks import enqueue_posts_for_new_case
from .utils.courtlistener import (
    get_docket_id_from_query,
    lookup_docket_by_cl_id,
)


def search(request: Request) -> Response:
    query = request.GET.get("q")
    context = {"query": query}
    try:
        docket_id = get_docket_id_from_query(query)
        data = lookup_docket_by_cl_id(docket_id)
        if data:
            context["docket_id"] = docket_id
            context["case_name"] = data["case_name"]
            context["channels"] = get_channel_groups_per_user(request.user.pk)
            template = "./includes/search_htmx/case-form.html"
            response = render(request, template, context)
            return trigger_client_event(
                response,
                "groupCheckbox",
                after="settle",
            )
    except HTTPError:
        template = "./includes/search_htmx/no-result.html"
    except ValidationError:
        template = "./includes/search_htmx/invalid-keyword.html"

    return render(request, template, context)


class AddCaseView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "./add-case.html")

    def post(self, request, *args, **kwargs):
        docket_id = request.POST.get("docketId")
        name = request.POST.get("name")
        case_summary = request.POST.get("caseSummary")

        try:
            docket = lookup_docket_by_cl_id(docket_id)
        except HTTPError:
            context = {
                "docket_id": docket_id,
                "case_name": name,
                "summary": case_summary,
                "error": "There was an error trying to submit the form. Please try again.",
            }
            template = "./includes/search_htmx/case-form.html"
            return render(request, template, context)

        docket["case_name"] = name
        docket["case_summary"] = case_summary
        subscription, created = create_or_update_subscription_from_docket(
            docket
        )
        channels = request.POST.getlist("channels")

        for channel_id in channels:
            subscription.channel.add(channel_id)

        if created:
            enqueue_posts_for_new_case(subscription)

        return render(request, "./includes/search_htmx/success.html")
