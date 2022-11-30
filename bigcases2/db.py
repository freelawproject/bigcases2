import json

import click
from flask import current_app, g
import psycopg2

from bigcases2.misc import lookup_court

DATABASE_SCHEMA_PATH = "../database/schema.sql"
BCB1_JSON_PATH = "../data/bigcases.json"

#####################################################################
# See https://flask.palletsprojects.com/en/2.2.x/tutorial/database/ #
#####################################################################


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host=current_app.config["DATABASE"]["HOSTNAME"],
            database=current_app.config["DATABASE"]["DATABASE"],
            user=current_app.config["DATABASE"]["USERNAME"],
            password=current_app.config["DATABASE"]["PASSWORD"],
        )
        current_app.logger.debug(f"Database connection: {g.db}")

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app):
    # https://flask.palletsprojects.com/en/2.2.x/tutorial/database/#register-with-the-application
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(load_bcb1_command)
    app.cli.add_command(empty_db_command)
    app.cli.add_command(export_db_command)


#####################################################################
# COMMANDS
#####################################################################


@click.command("init-db")
def init_db_command():
    """
    Initialize a new database
    """
    click.echo("Initializing database...")

    cur = get_db().cursor()
    with current_app.open_resource(DATABASE_SCHEMA_PATH) as f:
        click.echo(f)
        cur.execute(f.read().decode("utf8"))
        cur.connection.commit()
        cur.close()

    click.echo("Done initializing database.")


@click.command("load-bcb1")
def load_bcb1_command():
    """
    Import BCB1 cases from JSON file into the database
    https://github.com/bdheath/Big-Cases/blob/master/bigcases.json
    """
    click.echo("Loading Big Cases Bot v1 JSON file...")

    json_f = current_app.open_resource(BCB1_JSON_PATH)
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
        cur = get_db().cursor()
        cur.execute(
            'INSERT INTO "case" (court, case_number, bcb1_description, in_bcb1) VALUES(%s, %s, %s, %s)',
            (court_key, bcb1_case_number, bcb1_name, True),
        )

    # Commit DB transaction
    cur.connection.commit()
    cur.close()

    click.echo("Done.")


@click.command("empty-db")
def empty_db_command():
    """
    Delete data from DB but leave structure intact
    """
    click.echo("Emptying database...")

    q = 'DELETE FROM "case"'
    cur = get_db().cursor()
    cur.execute(q)
    cur.connection.commit()
    cur.close()

    click.echo(f"Done.")


@click.command()
def export_db_command():
    """
    Export a copy of the database
    """
    raise NotImplementedError


#####################################################################
# UTILITY FUNCTIONS
#####################################################################


def add_case(
    court: str,
    case_number: str,
    name: str,
    bcb1_name: str = None,
    cl_id: int = None,
    in_bcb1=False,
):

    # Write to DB
    cur = get_db().cursor()
    cur.execute(
        'INSERT INTO "case" (court, case_number, bcb1_description, cl_case_title, cl_docket_id, in_bcb1) VALUES(%s, %s, %s, %s, %s, %s)',
        (court, case_number, bcb1_name, name, cl_id, in_bcb1),
    )

    # Commit DB transaction
    cur.connection.commit()
    cur.close()
