from pprint import pformat

import click
import art  # https://www.4r7.ir/

from bigcases2.courtlistener import (
    lookup_docket_by_cl_id,
    court_url_to_key,
    get_case_from_cl,
)
from bigcases2.db import add_case


VERSION = "0.0.1"
HEADLINE_TEXT = "Big Cases Bot 2"
HEADLINE_FONT = "slant"
CL_BASE = "https://www.courtlistener.com"


@click.group()
def cli():
    pass


def headline():
    click.echo(art.text2art(HEADLINE_TEXT, font=HEADLINE_FONT))


@cli.command()
def info():
    """
    Display information about Big Cases Bot 2
    """
    headline()
    click.echo(f"bigcases2 version {VERSION}")


@cli.command()
def init():
    """
    Initialize!
    """
    # Init DB
    # Load BCB1 cases
    # Follow cases
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


def init_app(app):
    app.cli.add_command(info)
    app.cli.add_command(init)
    app.cli.add_command(lookup)
    app.cli.add_command(search_command)
    app.cli.add_command(add)
