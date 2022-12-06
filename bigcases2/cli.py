# from pprint import pformat
from os import uname

import click
import art  # https://www.4r7.ir/
from colors import color
from flask import current_app
from werkzeug.security import generate_password_hash

from bigcases2.courtlistener import (
    lookup_docket_by_cl_id,
    court_url_to_key,
    get_case_from_cl,
)
from bigcases2.db import add_case
from bigcases2.models import User, db


VERSION = "0.0.1"
HEADLINE_TEXT = "Big Cases Bot 2"
HEADLINE_FONT = "slant"
CL_BASE = "https://www.courtlistener.com"


@click.group()
def cli():
    pass


def headline():
    click.echo(color(art.text2art(HEADLINE_TEXT, font=HEADLINE_FONT), fg="green"))


@cli.command()
def info():
    """
    Display information about Big Cases Bot 2
    """
    headline()
    click.echo(f"bigcases2 version {VERSION}")
    click.echo(f"Environment: {current_app.config.get('ENV')}")
    click.echo(f"Database: {db.engine}")
    click.echo(f"Operating system: {uname().version}")


@cli.command()
def init():
    """
    Initialize!
    """
    # Init DB
    init_db_command()

    # Add some dev users if we're in dev
    if current_app.config.get("ENV") == "dev":
        bootstrap_dev_data_command()

    # TODO: Load BCB1 cases
    # TODO: Follow cases
    raise NotImplementedError


@cli.command()
@click.option("--add/--no-add", default=False)
def lookup(add):
    """
    Lookup a case in the RECAP archive by its CourtListener ID,
    and optionally add it.
    """
    dummy_cl_id = 63385389
    result = lookup_docket_by_cl_id(dummy_cl_id)
    # click.echo(pformat(result))
    court_url = result["court"]
    court = court_url_to_key(court_url)
    case_name = result["case_name"]
    docket_number = result["docket_number"]
    uri = result["absolute_url"]
    cl_url = f"{CL_BASE}{uri}"
    click.echo(f"Name: {case_name}")
    click.echo(f"Case no.: {docket_number}")
    click.echo(f"Court: {court}")
    click.echo(f"Link: {cl_url}")

    if add:
        click.echo("We'll try to add this case to the DB.")
        add_case(court, docket_number, case_name, dummy_cl_id)
        click.echo("Added!")


@click.command("search")
@click.argument("court")
@click.argument("case_number")
@click.option("--add/--no-add", default=None)
def search_command(court: str, case_number: str, add):
    """
    Search for a case in CourtListener, and optionally add it to the database.
    Example usage: flask --app bigcases2 search cand "22-cv-00123"
    """
    click.echo("cli.search() called")
    cl_result = get_case_from_cl(court, case_number)
    if cl_result:
        click.echo(
            f"Found it! -> {court} / {cl_result['docket_number']} / {cl_result['case_name']} / {cl_result['id']}"
        )

        if add is None:
            click.echo("Don't know if we want to add it yet.")
            add = click.confirm("Do you want to add it?")
            click.echo(f"add is now {add}")

        if add:
            click.echo("We'll try to add this case to the DB.")
            add_case(
                court,
                cl_result["docket_number"],
                cl_result["case_name"],
                cl_id=cl_result["id"],
            )
            click.echo("Added!")
    else:
        click.echo("No results.")


@cli.command()
def add():
    """
    Interactively add a new case
    """
    pass


@click.command("init-db")
def init_db_command():
    """
    Initialize a new database
    """
    click.echo("Initializing database...")

    from bigcases2.models import db

    with current_app.app_context():
        db.create_all()

    click.echo("Done initializing database.")
    # click.echo("Just kidding; we didn't do anything!")


@click.command("bootstrap-dev")
def bootstrap_dev_data_command():
    """
    Add some minimal information for development
    """
    new_users = []
    for user_info in current_app.config.get("BOOTSTRAP").get("USERS"):
        u = User(
            email=user_info["EMAIL"],
            password=generate_password_hash(user_info["PASSWORD"]),
        )
        u.enabled = True
        u.allow_login = True
        u.allow_spend = False
        u.allow_follow = True
        current_app.logger.debug(f"Creating new user for {u.email}")
        db.session.add(u)
        new_users.append(u)
    db.session.commit()
    current_app.logger.debug(f"New users: {new_users}")


def init_app(app):
    app.cli.add_command(info)
    app.cli.add_command(init)
    app.cli.add_command(lookup)
    app.cli.add_command(search_command)
    app.cli.add_command(add)
    app.cli.add_command(init_db_command)
    app.cli.add_command(bootstrap_dev_data_command)
