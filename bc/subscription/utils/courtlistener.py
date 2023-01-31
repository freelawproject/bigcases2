import logging

import courts_db
import requests
from django.conf import settings

from .exceptions import MultiDefendantCaseError

logger = logging.getLogger(__name__)

CL_API = {
    "docket": "https://www.courtlistener.com/api/rest/v3/dockets/",
    "docket-alerts": "https://www.courtlistener.com/api/rest/v3/docket-alerts/",
}


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


def auth_header() -> dict:
    token = settings.COURTLISTENER_API_KEY
    header_dict = {"Authorization": f"Token {token}"}
    return header_dict


def lookup_docket_by_cl_id(cl_id: int):
    """
    Performs a GET query on /api/rest/v3/dockets/
    to get a Docket using the CourtListener ID
    """
    url = f"{CL_API['docket']}{cl_id}/"
    response = requests.get(url, headers=auth_header(), timeout=5)
    response.raise_for_status()
    return response.json()


def lookup_docket_by_case_number(court: str, docket_number: str):
    """
    Performs a GET query on /api/rest/v3/dockets/
    using the court_id and docket_number to get a
    Docket.
    """

    response = requests.get(
        CL_API["docket"],
        params={"court_id": court, "docket_number": docket_number},
        headers=auth_header(),
        timeout=5,
    )
    data = response.json()
    num_results = data["count"]
    if num_results == 1:
        return data["results"][0]
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


def subscribe_to_docket_alert(cl_id: int) -> bool:
    """
    Performs a POST query on /api/rest/v3/docket-alerts/
    to subscribe to docket alerts for a given CourtListener docket ID.
    """
    response = requests.post(
        CL_API["docket-alerts"],
        headers=auth_header(),
        data={
            "docket": cl_id,
        },
        timeout=5,
    )

    try:
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as http_error:  # Treats all 400 or 500 HTTP status codes as HTTPError Exceptions
        print(
            f"Error subscribing to case {cl_id}: got HTTP response {http_error.status_code}"
        )
        return False


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
