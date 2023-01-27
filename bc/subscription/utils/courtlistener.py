import json
import logging
import re
from pprint import pformat
from typing import Union

import courts_db
import requests
from django.conf import settings

from .exceptions import MultiDefendantCaseError

logger = logging.getLogger(__name__)


API_ROOT = "https://www.courtlistener.com/api/rest/v3"
ENDPOINT_DOCKET_ALERTS = f"{API_ROOT}/docket-alerts/"


def lookup_court(court: str):
    """
    Lookup a court name or citation string using courts-db.
    Returns court ID (e.g., "cand" for "N.D. Cal.")
    Returns None if it can't find anything.
    """
    results = courts_db.find_court(court)
    if len(results) == 1:
        return results[0]
    elif len(results) == 0:
        print(f"No results for court '{court}'")
        return None
    else:
        print(f"Could not resolve court '{court}'")
        return None


def trim_docket_ending_number(s: str) -> str:
    """
    Trims weird numeric endings from BCB1 case numbers, like
    "-12" from "1:18-cr-00215-12"
    """
    ending_pattern = re.compile(r"\d+(-\d+)$")
    match = ending_pattern.search(s)
    if match:
        ending = match.groups()[0]
        length = len(ending)
        ret = s[:-length]
        return ret
    else:
        return s


def auth_header() -> dict:
    token = settings.COURTLISTENER_API_KEY
    header_dict = {"Authorization": f"Token {token}"}
    return header_dict


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
    response = requests.get(url, headers=auth_header())
    data = response.json()
    return data


def get_case_from_cl(court: str, case_number: str):
    url = f"{API_ROOT}/dockets/?court__id={court}&docket_number={case_number}"
    response = requests.get(url, headers=auth_header())
    data = response.json()
    ret = None

    num_results = data["count"]
    print(data["count"])
    if num_results == 1:
        ret = data["results"][0]
    elif num_results == 0:
        return None
    else:
        msg = f"Expected 0 or 1 results, but got {num_results}"

        # Produce some useful information for debugging, maybe
        pacer_ids = {}
        for result in data["results"]:
            cl_id = result["id"]
            pacer_id = result.get("pacer_case_id")
            pacer_ids[cl_id] = pacer_id
        raise MultiDefendantCaseError(msg)

        # RESULT: We have multiple CL dockets corresponding to
        # multiple PACER IDs :(
        #
        # See, e.g., nyed 1:09-cr-00466, which gives this mapping
        # of CL IDs to PACER IDs
        # {
        #     4319866: '294052',
        #     6146972: '294050',
        #     6360330: '294049',
        #     6452146: '294051',
        #     14197745: '294048',
        #     14569244: '294054',
        #     14665429: '294053'
        # }
        # The PACER IDs are all consecutive, from 294048 to 294054.
        # This is a criminal case with 6 defendants. Is that it?
        #
        # Aha. Yep. Brad had the case number "1:09-cr-00466-4". I'd trimmed the "-4".
        #
        # Notes in Issue: https://github.com/freelawproject/bigcases2/issues/18

        # TODO: Figure out how to choose the "best" of multiple dockets

    return ret


def get_docket_alert_subscriptions() -> list:
    """
    Performs a GET query on /api/rest/v3/docket-alerts/
    to get a list of CourtListener docket IDs to which
    we are subscribed.
    """
    response = requests.get(ENDPOINT_DOCKET_ALERTS, headers=auth_header())
    response_data = response.json()
    if response_data.get("count") == 0:
        return []
    filtered = [
        r for r in response_data["results"] if r.get("alert_type") == 1
    ]
    return filtered


def subscribe_to_docket_alert(cl_id: int) -> bool:
    """
    Performs a POST query on /api/rest/v3/docket-alerts/
    to subscribe to docket alerts for a given CourtListener docket ID.
    """
    response = requests.post(
        ENDPOINT_DOCKET_ALERTS,
        headers=auth_header(),
        data={
            "docket": cl_id,
        },
    )

    if response.status_code == 201:
        return True
    else:
        print(
            f"Error subscribing to case {cl_id}: got HTTP response {response.status_code}"
        )
        return False


def lookup_judge(judge_resource: str):
    """
    Query CL and return information about a judge.
    Input: judge_resource: a CL People resource URI like
    "https://www.courtlistener.com/api/rest/v3/people/664/"
    """
    response = requests.get(
        judge_resource,
        headers=auth_header(),
    )
    print(
        f"lookup_judge(): <{response.status_code}> for query to {judge_resource}"
    )
    response_data = response.json()
    print(pformat(response_data))
    return response_data


def handle_multi_defendant_cases(queue):
    logger.debug("handle_multi_defendant_cases(): started")
    for tpl in queue:
        court, case_number = tpl
        logger.debug(
            f"handle_multi_defendant_cases(): trying {court} {case_number}"
        )
        # TODO
        raise NotImplementedError
    logger.debug("handle_multi_defendant_cases(): done")


def add_case(
    court: str,
    case_number: str,
    name: str,
    bcb1_name: Union[str, None] = None,
    cl_id: Union[int, None] = None,
    in_bcb1: bool = False,
):
    raise NotImplementedError
