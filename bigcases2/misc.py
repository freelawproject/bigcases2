import re

import courts_db
from flask import current_app
from os import urandom

WEIRD_ENDING_PATTERN = r"\d+(-\d+)$"
WEIRD_ENDING_RE = re.compile(WEIRD_ENDING_PATTERN)


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


def trim_weird_ending(s: str) -> str:
    """
    Trims weird numeric endings from BCB1 case numbers, like
    "-12" from "1:18-cr-00215-12"
    """
    match = WEIRD_ENDING_RE.search(s)
    if match:
        current_app.logger.debug(f'Found a weird ending in "{s}"')
        ending = match.groups()[0]
        length = len(ending)
        ret = s[:-length]
        current_app.logger.debug(f'Trimmed to "{ret}"')
        return ret
    else:
        return s


def generate_key(length=32) -> str:
    return urandom(length).hex()


def add_case(
    court: str,
    case_number: str,
    name: str,
    bcb1_name: str = None,
    cl_id: int = None,
    in_bcb1=False,
):
    raise NotImplementedError


def update_case(bcb2_id: int, cl_id: int, cl_name: str):
    # update_query = (
    #     'UPDATE "case" SET cl_docket_id = %s, cl_case_title = %s WHERE id = %s'
    # )
    # with get_db().cursor() as cur:
    #     cur.execute(update_query, (cl_id, cl_name, bcb2_id))
    #     cur.connection.commit()
    raise NotImplementedError
