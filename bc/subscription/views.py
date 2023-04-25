from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views import View
from django_rq.queues import get_queue
from requests.exceptions import HTTPError
from rest_framework.request import Request
from rest_framework.response import Response
from rq import Retry

from bc.channel.selectors import get_enabled_channels
from bc.core.utils.status.templates import FOLLOW_A_NEW_CASE_TEMPLATE

from .services import create_or_update_subscription_from_docket
from .utils.courtlistener import (
    get_docket_id_from_query,
    lookup_docket_by_cl_id,
)

queue = get_queue("default")


def search(request: Request) -> Response:
    query = request.GET.get("q")
    context = {"query": query}
    try:
        docket_id = get_docket_id_from_query(query)
        data = lookup_docket_by_cl_id(docket_id)
        if data:
            context["docket_id"] = docket_id
            context["case_name"] = data["case_name"]
            template = "./includes/search_htmx/case-form.html"
        else:
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

        if created:
            for channel in get_enabled_channels():
                message, _ = FOLLOW_A_NEW_CASE_TEMPLATE.format(
                    docket=subscription.name_with_summary,
                    docket_link=subscription.cl_url,
                )

                api = channel.get_api_wrapper()

                queue.enqueue(
                    api.add_status,
                    message,
                    None,
                    retry=Retry(
                        max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                        interval=settings.RQ_RETRY_INTERVAL,
                    ),
                )

        return render(request, "./includes/search_htmx/success.html")
