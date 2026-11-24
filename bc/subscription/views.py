from collections.abc import Iterable

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
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


def get_curated_channels_or_403(
    user, requested_ids: Iterable[str] = ()
) -> list[Channel]:
    """
    Check that a user may add cases, and to the channels they asked for.

    The user must curate at least one channel, and every requested channel
    id must be one of theirs. Unknown or non-numeric ids fail the check.

    Args:
        user: the user making the request
        requested_ids: channel ids as submitted, e.g. from request.POST

    Returns:
        list[Channel]: the requested channels

    Raises:
        PermissionDenied: if any check fails
    """
    user_channels = {
        str(channel.pk): channel
        for channel in Channel.objects.filter(user=user)
    }
    requested = set(requested_ids)
    if not user_channels or not requested <= user_channels.keys():
        raise PermissionDenied
    return [user_channels[pk] for pk in requested]


@login_required
def search(request: Request) -> Response:
    # Lookups use our CourtListener token, so only curators may search.
    get_curated_channels_or_403(request.user)

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

    def render_form_with_error(self, request, context, selected_channels):
        """Re-render the case form, keeping the channels the user chose."""
        context["channels"] = get_channel_groups_per_user(request.user.pk)
        context["selected_channels"] = {c.pk for c in selected_channels}
        template = "./includes/search_htmx/case-form.html"
        response = render(request, template, context)
        # Wire up the group "All/None" buttons, as the search view does.
        return trigger_client_event(
            response,
            "groupCheckbox",
            after="settle",
        )

    def post(self, request, *args, **kwargs):
        docket_id = request.POST.get("docketId")

        # Check this before touching the DB: creating or updating a
        # subscription changes the name, summary and article URL that every
        # channel following the case uses in its posts.
        channels = get_curated_channels_or_403(
            request.user, request.POST.getlist("channels")
        )

        form = AddSubscriptionForm(request.POST)
        if not channels:
            form.add_error(None, "Select at least one channel.")
        if not form.is_valid():
            context = {"docket_id": docket_id, "form": form}
            if form.non_field_errors():
                context["error"] = " ".join(form.non_field_errors())
            return self.render_form_with_error(request, context, channels)

        try:
            docket = lookup_docket_by_cl_id(docket_id)
        except (HTTPError, ReadTimeout):
            context = {
                "docket_id": docket_id,
                "form": form,
                "error": "There was an error trying to submit the form. Please try again.",
            }
            return self.render_form_with_error(request, context, channels)

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

                # Verify that all templates produce valid post content
                for channel in channels:
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
                "error": (
                    "The combination of name, summary and article URL exceeds "
                    f"the maximum character limit for {channel.get_service_display()} "
                    "posts. Please try reducing the number of characters in the inputs."
                    "You can use abbreviations or remove unnecessary words. Once you "
                    "have made these changes, resubmit the form."
                ),
            }
            return self.render_form_with_error(request, context, channels)

        subscription.channel.add(*channels)

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
