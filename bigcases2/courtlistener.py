"""
CourtListener webhook
"""

from pprint import pformat

import requests

from flask import (
    Blueprint,
    # flash,
    # g,
    # redirect,
    # render_template,
    request,
    # url_for,
    current_app,
)

# from werkzeug.exceptions import abort

# from flask import Flask, request, Response

from bigcases2.db import get_db


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
    # TODO: 'Idempotency-Key: 59f1be59-e428-427a-a346-9cacded5c1d4'

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
        for requirement in REQUIRED_FIELDS:
            assert requirement in result

    current_app.logger.debug("Passed checks")

    # TODO: Actually do something with the request

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
    print(url)
    current_app.logger.debug(url)
    response = requests.get(url)
    print(response)
    data = response.json()
    current_app.logger.debug(pformat(data))
    print(pformat(data))
    # print()
    ret = None

    if data["count"] == 1:
        ret = data["results"][0]
    elif data["count"] == 0:
        pass
    else:
        pass

    return ret
