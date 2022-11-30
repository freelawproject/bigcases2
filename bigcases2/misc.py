import courts_db


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
