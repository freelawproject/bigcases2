"""
Loading data from original Big Cases Bot (BCB1)
"""

import json
from pprint import pformat

import click
from flask import current_app

from .models import db, Case, Judge
from .misc import lookup_court, trim_weird_ending, update_case
from .courtlistener import get_case_from_cl, lookup_judge
from .exceptions import MultiDefendantCaseError


DATABASE_SCHEMA_PATH = "../database/schema.sql"
BCB1_JSON_PATH = "../data/bigcases.json"
MATCH_LIMIT = 10  # 3000


#####################################################################
# COMMANDS
#####################################################################


@click.command("load-bcb1")
def load_bcb1_command():
    """
    Import BCB1 cases from JSON file into the database
    https://github.com/bdheath/Big-Cases/blob/master/bigcases.json
    """
    from .models import db, Case

    click.echo("Loading Big Cases Bot v1 JSON file...")

    json_f = current_app.open_resource(BCB1_JSON_PATH)
    bcb1_data = json.load(json_f)

    # Quick validations
    assert "supreme_court_cases" in bcb1_data
    assert "cases" in bcb1_data

    # TODO: Handle Supreme Court cases in "supreme_court_cases" key

    record_num = 0
    for bcb1_record in bcb1_data["cases"]:
        record_num += 1
        if record_num >= MATCH_LIMIT + 1:
            break

        for key in ("court", "name", "case_number"):
            assert key in bcb1_record
        bcb1_court = bcb1_record["court"]
        bcb1_case_number = bcb1_record["case_number"]
        bcb1_name = bcb1_record["name"]

        # Handle erroneous "D. Ore." in original data
        if bcb1_court == "D. Ore.":
            bcb1_court = "D. Or."

        # Handle stray stuff at end of case numbers, e.g., "1:19-cr-00366-1"
        bcb1_case_number = trim_weird_ending(bcb1_case_number)

        court_key = lookup_court(bcb1_court)  # Transform to courts-db format
        print(
            f"BCB1 court: {bcb1_record['court']} / courts-db key: {court_key} / case_number: {bcb1_case_number}"
        )
        print(bcb1_name)

        # Write to DB
        c = Case(
            court=court_key,
            case_number=bcb1_case_number,
            bcb1_description=bcb1_name,
            in_bcb1=True,
        )
        db.session.add(c)

    # Commit DB transaction
    db.session.commit()

    click.echo("Done.")


@click.command("match-bcb1-cases")
def match_bcb1_cases_command():
    """
    Match cases in the BCB1 database with CourtListener
    """

    exceptions = []
    click.echo(f"Matching up to {MATCH_LIMIT} BCB1 cases to CourtListener...")

    stmt = (
        db.select(Case)
        .where(Case.in_bcb1 == True)
        .where(Case.cl_docket_id == None)
    )
    click.echo(stmt)

    row_num = 0

    db_result = db.session.execute(stmt)
    for case in db_result.scalars():
        row_num += 1
        if row_num >= MATCH_LIMIT + 1:
            break
        click.echo(f"#{row_num}: {case}")

        case.case_number = trim_weird_ending(case.case_number)
        cl_case = None
        try:
            cl_case = get_case_from_cl(case.court, case.case_number)
        except Exception as e:
            e_record = [
                e,
                case.court,
                case.case_number,
            ]
            exceptions.append(e_record)

        if cl_case:
            current_app.logger.debug("Got a case from CL...")
            current_app.logger.debug(pformat(cl_case))
            cl_docket_id = cl_case["id"]
            cl_nos_code = cl_case["nature_of_suit"]
            cl_court_uri = cl_case[
                "court"
            ]  # "https://www.courtlistener.com/api/rest/v3/courts/mad/"
            cl_case_name = cl_case["case_name"]
            assert cl_court_uri.endswith(f"/courts/{case.court}/")
            click.echo(
                f"Got a case for {case.court} {case.case_number}: {cl_docket_id}, NOS={cl_nos_code}"
            )
            click.echo(pformat(cl_case))

            # Update in DB
            case.cl_docket_id = cl_docket_id
            case.cl_case_title = cl_case_name
            case.cl_slug = cl_case["slug"]

            # Add judges
            if cl_case.get("assigned_to") not in (None, ""):
                cl_judge = lookup_judge(cl_case.get("assigned_to"))  # "assigned_to" will be in the form of a full CL resource URL like "https://www.courtlistener.com/api/rest/v3/people/664/"
                j = Judge.from_json(cl_judge)
                j.cases.append(case)
            if cl_case.get("referred_to") not in (None, ""):
                cl_judge = lookup_judge(cl_case.get("referred_to"))
                j = Judge.from_json(cl_judge)
                j.cases.append(case)

            db.session.commit()

    # Shunt multi-defendant cases into a queue for separate handling.
    # Probably not worth the effort for a few 1-off imports, but this
    # could be Cerlery-ized later.

    retry_multi_defendant_queue = []

    if len(exceptions) > 0:
        current_app.logger.error("*" * 50)
        current_app.logger.error(f"ENCOUNTERED {len(exceptions)} EXCEPTIONS:")
        for e_record in exceptions:
            e_, e_court, e_case_number = e_record
            if isinstance(e_, MultiDefendantCaseError):
                retry_multi_defendant_queue.append((e_court, e_case_number))
                current_app.logger.info(
                    f"Added to multi-defendant retry queue: {e_court} {e_case_number}"
                )
            current_app.logger.error("*" * 50)
            current_app.logger.error(pformat(e_record))
        current_app.logger.error("*" * 50)

    num_to_retry = len(retry_multi_defendant_queue)
    if num_to_retry > 0:
        current_app.logger.info(
            f"There are {num_to_retry} cases to retry as multi-defendant cases."
        )
        handle_multi_defendant_cases(retry_multi_defendant_queue)

    click.echo("Done.")


def handle_multi_defendant_cases(queue):
    current_app.logger.debug("handle_multi_defendant_cases(): started")
    for tpl in queue:
        court, case_number = tpl
        current_app.logger.debug(
            f"handle_multi_defendant_cases(): trying {court} {case_number}"
        )
        # TODO
        raise NotImplementedError
    current_app.logger.debug("handle_multi_defendant_cases(): done")


def init_app(app):
    app.cli.add_command(load_bcb1_command)
    app.cli.add_command(match_bcb1_cases_command)
