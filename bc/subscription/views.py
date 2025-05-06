from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render
from django.views import View
from django_htmx.http import trigger_client_event
from django_rq.queues import get_queue
from requests.exceptions import HTTPError, ReadTimeout
from rest_framework.request import Request
from rest_framework.response import Response
from rq import Retry

from bc.channel.models import Channel
from bc.channel.selectors import get_channel_groups_per_user
from bc.core.utils.status.base import InvalidTemplate
from bc.core.utils.status.selectors import get_new_case_template

from .forms import AddSubscriptionForm
from .services import create_or_update_subscription_from_docket
from .tasks import check_initial_complaint_before_posting
from .utils.courtlistener import (
    get_docket_id_from_query,
    lookup_docket_by_cl_id,
    subscribe_to_docket_alert,
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
        try:
            with (
                transaction.atomic()
            ):  # Inner atomic block, create a savepoint
                (
                    subscription,
                    created,
                ) = create_or_update_subscription_from_docket(docket)
                channels = request.POST.getlist("channels")

                # Verify that all templates produce valid post content
                for channel_id in channels:
                    channel = Channel.objects.get(pk=channel_id)
                    template = get_new_case_template(channel.service)

                    template.format(
                        docket=subscription.name_with_summary,
                        docket_link=subscription.cl_url,
                        docket_id=subscription.cl_docket_id,
                        article_url=subscription.article_url,
                    )

                    if not template.is_valid:
                        raise InvalidTemplate
        except InvalidTemplate:
            context = {
                "docket_id": docket_id,
                "form": form,
                "channels": get_channel_groups_per_user(request.user.pk),
                "error": (
                    "The combination of name, summary and article URL exceeds "
                    f"the maximum character limit for {channel.get_service_display()} "
                    "posts. Please try reducing the number of characters in the inputs."
                    "You can use abbreviations or remove unnecessary words. Once you "
                    "have made these changes, resubmit the form."
                ),
            }
            template = "./includes/search_htmx/case-form.html"
            return render(request, template, context)

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

        queue.enqueue(
            subscribe_to_docket_alert,
            docket["id"],
            retry=Retry(
                max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                interval=settings.RQ_RETRY_INTERVAL,
            ),
        )

        return render(request, "./includes/search_htmx/success.html")
