from courts_db import find_court_by_id
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from .models import Docket


def view_docket(request: HttpRequest, docket_id: int) -> HttpResponse:
    docket = get_object_or_404(Docket, pk=docket_id)

    court_name = None
    court_results = find_court_by_id(docket.court)
    if len(court_results) == 1:
        court_name = court_results[0]["name"]

    context = {
        "docket": docket,
        "court_name": court_name,
    }
    return TemplateResponse(request, "docket.html", context)


def count_dockets(request: HttpRequest) -> HttpResponse:
    dockets = Docket.objects.count()

    context = {"dockets_count": dockets}

    return TemplateResponse(request, "homepage.html", context)


# @bp.route("/webhooks/docket", methods=["POST"])
# def cl_webhook():
#     """
#     Receives a docket alert webhook from CourtListener.
#     """
#     current_app.logger.debug("CL webhook hit")
#     data = request.json
#
#     # Check headers
#     current_app.logger.debug(f"Request headers: {pformat(request.headers)}")
#
#     # 'Content-Type: application/json'
#     assert "Content-Type" in request.headers
#     assert request.headers.get("Content-Type") == "application/json"
#
#     # Idempotency key
#     # 'Idempotency-Key: 59f1be59-e428-427a-a346-9cacded5c1d4'
#     idempotency_key = request.headers.get("Idempotency-Key")
#     assert idempotency_key is not None
#     # TODO: Actually check that we haven't recevied this key before
#
#     # Check request body
#     assert "webhook" in data
#     assert "version" in data["webhook"]
#     assert (
#         data["webhook"]["version"] == 1
#     )  # Handle other versions when they come into existence
#     assert "event_type" in data["webhook"]
#     assert (
#         data["webhook"]["event_type"] == 1
#     )  # Just docket alerts for this endpoint
#     assert "results" in data
#
#     results = data["results"]
#
#     for result in results:
#         # Check the result
#         for requirement in REQUIRED_FIELDS:
#             assert requirement in result
#
#         # TODO: Store docket entry in DB
#
#         # Handle any documents attached
#         if "recap_documents" in result and len(result["recap_documents"] > 0):
#             for doc in result["recap_documents"]:
#                 pass
#
#         # TODO: Actually do something with this docket entry
#
#     # TODO: Send 201 Created HTTP status
#     # TODO: Return real data, like an our ID of a created record
#     return {
#         "status": "ok",
#     }
