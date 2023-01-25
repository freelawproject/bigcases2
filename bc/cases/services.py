from .models import Docket
from .selectors import get_docket_by_case_number
from .utils.courtlistener import (
    court_url_to_key,
    lookup_judge,
    trim_docket_ending_number,
)


def docket_to_case(docket):
    """
    Creates a new Docket record for a given Docket from the CL API.
    Call get_case_from_cl() to get a Docket first.
    """
    cl_docket_id = docket["id"]
    cl_court_uri = docket["court"]
    cl_case_name = docket["case_name"]
    court_key = court_url_to_key(cl_court_uri)  # Transform to courts-db format
    docket_number = docket["docket_number"]

    # Trim unless it's a bankruptcy case; they don't have a "-cv-" part
    if not court_key.endswith("b"):
        docket_number = trim_docket_ending_number(docket_number)

    case_result = get_docket_by_case_number(
        docket_number=docket_number, court_key=court_key
    )

    if case_result:
        return case_result

    case = Docket.objects.create(
        court=court_key,
        docket_number=docket_number,
        cl_case_title=cl_case_name,
        cl_docket_id=cl_docket_id,
        cl_slug=docket["slug"],
    )

    cl_judge = None
    if docket.get("assigned_to"):
        cl_judge = lookup_judge(docket.get("assigned_to"))
    if docket.get("referred_to"):
        cl_judge = lookup_judge(docket.get("referred_to"))

    return case
