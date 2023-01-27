import logging
from pprint import pformat

from django.http import HttpRequest, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .api_serializers import WebhookSerializer

logger = logging.getLogger(__name__)


@api_view(["POST"])
def handle_cl_webhook(request: HttpRequest) -> HttpResponse:
    """
    Receives a docket alert webhook from CourtListener.
    """
    logger.debug("CL webhook hit")
    data = request.json

    # Check headers
    logger.debug(f"Request headers: {pformat(request.headers)}")

    # 'Content-Type: application/json'
    assert "Content-Type" in request.headers
    assert request.headers.get("Content-Type") == "application/json"

    # Idempotency key
    # 'Idempotency-Key: 59f1be59-e428-427a-a346-9cacded5c1d4'
    idempotency_key = request.headers.get("Idempotency-Key")
    assert idempotency_key is not None
    # TODO: Actually check that we haven't recevied this key before

    # Check request body
    assert "webhook" in data
    assert "version" in data["webhook"]
    assert (
        data["webhook"]["version"] == 1
    )  # Handle other versions when they come into existence
    assert "event_type" in data["webhook"]
    assert (
        data["webhook"]["event_type"] == 1
    )  # Just docket alerts for this endpoint
    assert "results" in data

    results = data["results"]

    for result in results:
        # Check the result
        serializer = WebhookSerializer(data=result)
        if serializer.is_valid():
            serialized_data = serializer.data
        else:
            logger.debug(f"Validation errors: {pformat(serializer.errors)}")
            continue
        # TODO: Store docket entry in DB

        # Handle any documents attached
        for doc in serialized_data["recap_documents"]:
            pass

        # TODO: Actually do something with this docket entry

    # TODO: Send 201 Created HTTP status
    # TODO: Return real data, like an our ID of a created record
    return Response(status=status.HTTP_201_CREATED)
