from datetime import timedelta
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django_rq.queues import get_queue
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from .api_permissions import WhitelistPermission
from .models import FilingUpdate
from .tasks import process_filing_update

queue = get_queue("default")


@api_view(["POST"])
@permission_classes([WhitelistPermission])
def handle_cl_webhook(request: Request) -> Response:
    """
    Receives a docket alert webhook from CourtListener.
    """

    idempotency_key = request.headers.get("Idempotency-Key")
    assert (
        idempotency_key is not None
    ), "Idempotency key has not been specified"

    data = request.data
    assert data["webhook"]["event_type"] == 1, "Webhook type not supported"

    cache_idempotency_key = cache.get(idempotency_key)
    if cache_idempotency_key:
        return Response(status=HTTPStatus.OK)

    for result in data["payload"]["results"]:
        cl_docket_id = result["docket"]
        for doc in result["recap_documents"]:
            filing = FilingUpdate.objects.create(
                docket_id=cl_docket_id,
                pacer_doc_id=doc["pacer_doc_id"],
                document_number=doc["document_number"],
                attachment_number=doc["attachment_number"]
                if doc["attachment_number"]
                else 0,
            )

            queue.enqueue_in(
                timedelta(seconds=settings.WEBHOOK_DELAY_TIME),
                process_filing_update,
                filing.pk,
            )

    """ Save the idempotency key for two days after the webhook is handled """
    cache.set(idempotency_key, True, 60 * 60 * 24 * 2)

    return Response(request.data, status=HTTPStatus.CREATED)
