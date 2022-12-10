"""
CourtListener webhook
"""

from pprint import pformat

import requests

from flask import (
    Blueprint,
    request,
    current_app,
)


API_ROOT = "https://www.courtlistener.com/api/rest/v3"

REQUIRED_FIELDS = (
    # TODO: Validate against a schema instead.
    "id",  # 2208776613
    "date_filed",  # "2022-10-11"
    "description",  # "MOTION for Settlement Preliminary Approval by ALLIANCE FOR JUSTICE, NATIONAL CONSUMER LAW CENTER, NATIONAL VETERANS LEGAL SERVICES PROGRAM. (Attachments: # 1 Text of Proposed Order Proposed Order)(Gupta, Deepak) (Entered: 10/11/2022)"
    "date_created",  # "2022-10-11T14:21:40.855097-07:00"
    "entry_number",  # 140
    "date_modified",  # "2022-10-18T13:03:18.466039-07:00"
    "recap_documents",  # list of dicts
    "pacer_sequence_number",  # 584
    "recap_sequence_number",  # "2022-10-11.001"
)

bp = Blueprint("courtlistener", __name__)


@bp.route("/webhooks/docket", methods=["POST"])
def cl_webhook():
    """
    Receives a docket alert webhook from CourtListener.
    """
    current_app.logger.debug("CL webhook hit")
    data = request.json

    # Check headers
    current_app.logger.debug(f"Request headers: {pformat(request.headers)}")

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
        for requirement in REQUIRED_FIELDS:
            assert requirement in result

        # TODO: Store docket entry in DB

        # Handle any documents attached
        if "recap_documents" in result and len(result["recap_documents"] > 0):
            for doc in result["recap_documents"]:
                pass

        # TODO: Actually do something with this docket entry

    # TODO: Send 201 Created HTTP status
    # TODO: Return real data, like an our ID of a created record
    return {
        "status": "ok",
    }


def auth_header() -> dict:
    token = current_app.config.get("COURTLISTENER").get("CL_API_KEY")
    return {"Authorization": f"Token {token}"}


def court_url_to_key(url: str) -> str:
    """
    Converts a court URL, which is returned by the CourtListner API,
    into the short version.
    Example: "https://www.courtlistener.com/api/rest/v3/courts/vawd/"
             converts to "vawd"
    """
    tokens = url.split("/")
    key = tokens[-2]
    return key


def lookup_docket_by_cl_id(cl_id: int):
    url = f"{API_ROOT}/dockets/{cl_id}/"
    # print(url)
    response = requests.get(url)
    # print(response)
    data = response.json()
    return data


def get_case_from_cl(court: str, case_number: str):
    url = f"{API_ROOT}/dockets/?court__id={court}&docket_number={case_number}"
    # print(url)
    current_app.logger.debug(url)
    response = requests.get(url)
    print(response)
    data = response.json()
    current_app.logger.debug(pformat(data))
    # print(pformat(data))
    ret = None

    num_results = data["count"]
    if num_results == 1:
        current_app.logger.debug("Returning 1 result.")
        ret = data["results"][0]
    elif num_results == 0:
        return None
    else:
        raise ValueError(f"Expected 0 or 1 results, but got {num_results}")

    return ret


def init_app(app):
    pass  # Nothing to do here yet
