import json
import sqlite3

import click
from flask import current_app, g

import courts_db

BCB1_JSON_PATH = "../data/bigcases.json"

#####################################################################
# See https://flask.palletsprojects.com/en/2.2.x/tutorial/database/ #
#####################################################################


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    current_app.logger.info("db.init_db() called.")
    click.echo("db.init_db() called")
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        click.echo(f)
        db.executescript(f.read().decode("utf8"))

    current_app.logger.info("db.init_db() done.")


@click.command("init-db")
def init_db_command():
    """
    Initialize a new database
    """
    click.echo("db.init_db_command() called")
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    # https://flask.palletsprojects.com/en/2.2.x/tutorial/database/#register-with-the-application
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(empty_db_command)


#####################################################################


def lookup_court(court: str):
    results = courts_db.find_court(court)
    if len(results) == 1:
        return results[0]
    elif len(results) == 0:
        print(f"No results for court '{court}'")
        return None
    else:
        print(f"Could not resolve court '{court}'")
        return None


def truncate_db():
    q = "DELETE FROM cases"
    result = g.db.execute(q)
    num_rows = result.rowcount
    return num_rows


def load_bcb1_json():
    """
    Load the JSON file from the original Big Cases Bot
    https://github.com/bdheath/Big-Cases/blob/master/bigcases.json
    """
    json_f = open(BCB1_JSON_PATH, "r")
    bcb1_data = json.load(json_f)

    # Quick validations
    assert "supreme_court_cases" in bcb1_data
    assert "cases" in bcb1_data

    # TODO: Handle Supreme Court cases in "supreme_court_cases" key

    for bcb1_record in bcb1_data["cases"]:
        for key in ("court", "name", "case_number"):
            assert key in bcb1_record
        bcb1_court = bcb1_record["court"]
        bcb1_case_number = bcb1_record["case_number"]
        bcb1_name = bcb1_record["name"]

        # Handle erroneous "D. Ore." in original data
        if bcb1_court == "D. Ore.":
            bcb1_court = "D. Or."

        # Handle stray "-1" at end of case numbers, e.g., "1:19-cr-00366-1"
        # TODO: Use regex instead; there are some -4's and other numbers. Why?? Who knows.
        if bcb1_case_number.endswith("-1"):
            print("** ends in -1 **")
            bcb1_case_number = bcb1_case_number.rstrip("-1")

        court_key = lookup_court(bcb1_court)  # Transform to courts-db format
        print(
            f"BCB1 court: {bcb1_record['court']} / courts-db key: {court_key} / case_number: {bcb1_case_number}"
        )
        print(bcb1_name)

        # Write to DB
        g.db.execute(
            "INSERT INTO cases (court, case_number, bcb1_description, in_bcb1) VALUES(?, ?, ?, ?)",
            (court_key, bcb1_case_number, bcb1_name, 1),
        )

    # Commit DB transaction
    g.db.commit()


def add_case(
    court: str,
    case_number: str,
    name: str,
    bcb1_name: str = None,
    cl_id: int = None,
    in_bcb1=0,
):

    # Write to DB
    g.db.execute(
        "INSERT INTO cases (court, case_number, bcb1_description, cl_case_title, cl_docket_id, in_bcb1) VALUES(?, ?, ?, ?, ?, ?)",
        (court, case_number, bcb1_name, name, cl_id, in_bcb1),
    )

    # Commit DB transaction
    g.db.commit()


@click.command("empty-db")
def empty_db_command():
    """
    Delete data from DB but leave structure intact
    """
    click.echo("Emptying database...")
    num_rows = truncate_db()
    click.echo(f"Done. Deleted {num_rows} rows.")


@click.command()
def load_db():
    """
    Load database from BCB1 JSON file
    """
    click.echo("Loading Big Cases Bot v1 JSON file...")
    load_bcb1_json()
    click.echo("Done.")


@click.command()
def export_db():
    """
    Export database to a CSV file
    """
    pass
