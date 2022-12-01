import re

import courts_db
from flask import current_app


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
