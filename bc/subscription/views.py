from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views import View
from django_htmx.http import trigger_client_event
from django_rq.queues import get_queue
from requests.exceptions import HTTPError, ReadTimeout
from rest_framework.request import Request
from rest_framework.response import Response
from rq import Retry

from bc.channel.selectors import get_channel_groups_per_user

from .forms import AddSubscriptionForm
from .services import create_or_update_subscription_from_docket
from .tasks import check_initial_complaint_before_posting
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
            context["form"] = AddSubscriptionForm(
                initial={"docket_name": data["case_name"]}
            )
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
    except ReadTimeout:
        template = "./includes/search_htmx/time-out.html"

    return render(request, template, context)


class AddCaseView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "./add-case.html")

    def post(self, request, *args, **kwargs):
        docket_id = request.POST.get("docketId")
        form = AddSubscriptionForm(request.POST)
        if not form.is_valid():
            context = {"docket_id": docket_id, "form": form}
            template = "./includes/search_htmx/case-form.html"
            return render(request, template, context)

        try:
            docket = lookup_docket_by_cl_id(docket_id)
        except (HTTPError, ReadTimeout):
            context = {
                "docket_id": docket_id,
                "form": form,
                "error": "There was an error trying to submit the form. Please try again.",
            }
            template = "./includes/search_htmx/case-form.html"
            return render(request, template, context)

        cd = form.cleaned_data
        docket["case_name"] = cd["docket_name"]
        docket["case_summary"] = cd["case_summary"]
        docket["article_url"] = cd["article_url"]
        subscription, created = create_or_update_subscription_from_docket(
            docket
        )
        channels = request.POST.getlist("channels")

        for channel_id in channels:
            subscription.channel.add(channel_id)

        if created:
            queue.enqueue(
                check_initial_complaint_before_posting,
                subscription.pk,
                retry=Retry(
                    max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                    interval=settings.RQ_RETRY_INTERVAL,
                ),
            )

        return render(request, "./includes/search_htmx/success.html")
