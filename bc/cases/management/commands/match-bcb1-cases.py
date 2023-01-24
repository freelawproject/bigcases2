import logging
from pprint import pformat

import click
from django.conf import settings
from django.core.management.base import BaseCommand

from bc.cases.selectors import get_dockets_from_bcb1
from bc.cases.utils.courtlistener import (
    get_case_from_cl,
    handle_multi_defendant_cases,
    lookup_judge,
    trim_docket_ending_number,
)
from bc.cases.utils.exceptions import MultiDefendantCaseError
from bc.people.models import Judge

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Match cases in the BCB1 database with CourtListener"

    def handle(self, *args, **options):
        exceptions = []
        click.echo(
            f"Matching up to {settings.BCB_MATCH_LIMIT} BCB1 cases to CourtListener..."
        )

        bcb1_dockets = get_dockets_from_bcb1()

        for case in bcb1_dockets:
            case.docket_number = trim_docket_ending_number(case.docket_number)
            cl_case = None
            try:
                cl_case = get_case_from_cl(case.court, case.docket_number)
            except Exception as e:
                e_record = [
                    e,
                    case.court,
                    case.docket_number,
                ]
                exceptions.append(e_record)
            if cl_case:
                logger.debug("Got a case from CL...")

                ## Refactor from here --v

                cl_docket_id = cl_case["id"]
                cl_nos_code = cl_case["nature_of_suit"]
                cl_court_uri = cl_case["court"]
                cl_case_name = cl_case["case_name"]
                assert cl_court_uri.endswith(f"/courts/{case.court}/")
                click.echo(
                    f"Got a case for {case.court} {case.docket_number}: {cl_docket_id}, NOS={cl_nos_code}"
                )

                # Update in DB
                case.cl_docket_id = cl_docket_id
                case.cl_case_title = cl_case_name
                case.cl_slug = cl_case["slug"]
                case.save()

                # Add judges
                cl_judge = None
                if cl_case.get("assigned_to") not in (None, ""):
                    cl_judge = lookup_judge(cl_case.get("assigned_to"))
                if cl_case.get("referred_to") not in (None, ""):
                    cl_judge = lookup_judge(cl_case.get("referred_to"))

                j = Judge.from_json(cl_judge)
                j.cases.add(case)
                ## Refactor to here --^

        # Shunt multi-defendant cases into a queue for separate handling.
        # Probably not worth the effort for a few 1-off imports, but this
        # could be Cerlery-ized later.

        retry_multi_defendant_queue = []

        if len(exceptions) > 0:
            logger.error("*" * 50)
            logger.error(f"ENCOUNTERED {len(exceptions)} EXCEPTIONS:")
            for e_record in exceptions:
                e_, e_court, e_case_number = e_record
                if isinstance(e_, MultiDefendantCaseError):
                    retry_multi_defendant_queue.append(
                        (e_court, e_case_number)
                    )
                    logger.info(
                        f"Added to multi-defendant retry queue: {e_court} {e_case_number}"
                    )
                logger.error("*" * 50)
                logger.error(pformat(e_record))
            logger.error("*" * 50)

        num_to_retry = len(retry_multi_defendant_queue)
        if num_to_retry > 0:
            logger.info(
                f"There are {num_to_retry} cases to retry as multi-defendant cases."
            )
            handle_multi_defendant_cases(retry_multi_defendant_queue)

        print("Done.")
