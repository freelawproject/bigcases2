import logging
import re
from typing import TypedDict

import courts_db
import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .exceptions import MultiDefendantCaseError

logger = logging.getLogger(__name__)

# Regex expression to match dockets and documents URL from CL. ie:
#   https://www.courtlistener.com/docket/65745614/united-states-v-ward/
#   https://www.courtlistener.com/docket/65364032/6/1/antonyuk-v-hochul/
DOCKET_URL_PATTERN = re.compile(
    r"(?:www\.courtlistener\.com\/docket\/)(?P<docket_id>\d+)(?:\/.*)"
)

# Regex expression to match PDF URLs from CL. ie:
#   https://storage.courtlistener.com/recap/gov.uscourts.dcd.178502/gov.uscourts.dcd.178502.1.0_48.pdf
#   https://storage.courtlistener.com/recap/gov.uscourts.cand.373179/gov.uscourts.cand.373179.1.0.pdf
PDF_URL_PATTERN = re.compile(
    r"(?P<url_for_redirect>(https:\/{2}storage\.courtlistener\.com\/recap\/gov.uscourts.(?P<court>[a-z]+).(?P<pacer_case_id>\d+)))(?:\/.*)"
)

CL_API = {
    "docket": "https://www.courtlistener.com/api/rest/v3/dockets/",
    "docket-alerts": "https://www.courtlistener.com/api/rest/v3/docket-alerts/",
    "recap-documents": "https://www.courtlistener.com/api/rest/v3/recap-documents/",
    "recap-fetch": "https://www.courtlistener.com/api/rest/v3/recap-fetch/",
    "media-storage": "https://storage.courtlistener.com/",
}

pacer_to_cl_ids = {
    # Maps PACER ids to their CL equivalents
    "azb": "arb",  # Arizona Bankruptcy Court
    "cofc": "uscfc",  # Court of Federal Claims
    "neb": "nebraskab",  # Nebraska Bankruptcy
    "nysb-mega": "nysb",  # Remove the mega thing
}

# Reverse dict of pacer_to_cl_ids
cl_to_pacer_ids = {v: k for k, v in pacer_to_cl_ids.items() if v != "nysb"}


def map_pacer_to_cl_id(pacer_id):
    return pacer_to_cl_ids.get(pacer_id, pacer_id)


def map_cl_to_pacer_id(cl_id):
    return cl_to_pacer_ids.get(cl_id, cl_id)


def get_docket_id_from_query(query: str) -> int:
    """Returns the docket id extracted from the search query

    Args:
        query (str): the query string provided by the curators using the search bar

    Raises:
        ValidationError: if the provided string is not a number or a valid URL.

    Returns:
        int: the docket id
    """
    cleaned_str = query.strip()
    if cleaned_str.isnumeric():
        return int(cleaned_str)

    # check if the query string is a valid URL
    validator = URLValidator()
    validator(cleaned_str)

    # check if the query string is a PDF link
    is_pdf_link = re.search(PDF_URL_PATTERN, cleaned_str)
    if is_pdf_link:
        r = requests.get(is_pdf_link.group("url_for_redirect"))
        r.raise_for_status()
        cleaned_str = r.url

    # check if the query string is a CL docket link or a CL PDF link
    is_docket_link = re.search(DOCKET_URL_PATTERN, cleaned_str)
    if is_docket_link:
        return int(is_docket_link.group("docket_id"))

    raise ValidationError("The query string provided is invalid")


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


class DocumentDict(TypedDict):
    page_count: int
    filepath_local: str


def lookup_document_by_doc_id(doc_id: int | None) -> DocumentDict:
    """
    Performs a GET query on /api/rest/v3/recap-documents/
    using the document_id to get a recap document
    """
    response = requests.get(
        f"{CL_API['recap-documents']}{doc_id}/",
        params={"fields": "filepath_local,page_count"},
        headers=auth_header(),
        timeout=5,
    )
    response.raise_for_status()
    data: DocumentDict = response.json()
    return data


def download_pdf_from_cl(filepath: str) -> bytes:
    document_url = f"{CL_API['media-storage']}{filepath}"
    document_request = requests.get(document_url, timeout=3)
    document_request.raise_for_status()
    return document_request.content


def purchase_pdf_by_doc_id(doc_id: int | None) -> int:
    """
    Performs a POST query on /api/rest/v3/recap-fetch/
    using the document_id from CL and the PACER's login
    credentials.
    """
    response = requests.post(
        f"{CL_API['recap-fetch']}",
        json={
            "request_type": 2,
            "pacer_username": settings.PACER_USERNAME,
            "pacer_password": settings.PACER_PASSWORD,
            "recap_document": doc_id,
        },
        headers=auth_header(),
        timeout=5,
    )
    response.raise_for_status()
    data = response.json()
    return data["id"]


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
    except requests.exceptions.HTTPError as err:
        print(
            f"Error subscribing to case {cl_id}: got HTTP response {err.response.status_code}"
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
