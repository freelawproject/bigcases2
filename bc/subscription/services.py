from courts_db import find_court_by_id

from .models import Subscription


def create_or_update_subscription_from_docket(docket):
    """
    Creates or updates a Subscription record for a given Docket from the CL API.
    """
    pacer_case_id = docket["pacer_case_id"]

    docket_name = docket["case_name"]
    docket_number = docket["docket_number"]

    cl_docket_id = docket["id"]
    cl_court_id = docket["court_id"]
    cl_slug = docket["slug"]

    court = find_court_by_id(cl_court_id)
    court_name = court[0]["name"] if len(court) == 1 else ""

    return Subscription.objects.update_or_create(
        cl_docket_id=cl_docket_id,
        defaults={
            "docket_name": docket_name,
            "docket_number": docket_number,
            "cl_court_id": cl_court_id,
            "cl_slug": cl_slug,
            "pacer_case_id": pacer_case_id,
            "court_name": court_name,
        },
    )
