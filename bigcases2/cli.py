# from pprint import pformat
from os import uname
import json
from pprint import pformat

import click
import art  # https://www.4r7.ir/
from colors import color
from flask import current_app
from werkzeug.security import generate_password_hash
from prettytable import PrettyTable

from .courtlistener import (
    lookup_docket_by_cl_id,
    court_url_to_key,
    get_case_from_cl,
    get_docket_alert_subscriptions,
    subscribe_to_docket_alert,
    docket_to_case,
)
from .misc import add_case
from .models import db, User, Beat, Channel
from .masto import get_mastodon


VERSION = "0.0.1"
HEADLINE_TEXT = "Big Cases Bot 2"
HEADLINE_FONT = "slant"
CL_BASE = "https://www.courtlistener.com"


def headline():
    click.echo(
        color(art.text2art(HEADLINE_TEXT, font=HEADLINE_FONT), fg="green")
    )


@click.command("info")
def info_command():
    """
    Display information about Big Cases Bot 2
    """
    headline()
    click.echo(f"bigcases2 version {VERSION}")
    click.echo(f"Environment: {current_app.config.get('ENV')}")
    click.echo(f"Database: {db.engine}")
    click.echo(f"Operating system: {uname().version}")


@click.command("init")
def init_command():
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
    # raise NotImplementedError


@click.command("init-db")
def init_db_command():
    """
    Initialize a new database
    """
    click.echo("Initializing database...")

    db.create_all()

    click.echo("Done initializing database.")


@click.command("empty-db")
def empty_db_command():
    """
    Delete data from DB but leave structure intact
    """
    # TODO: Move this command to models.py

    click.echo("Emptying database...")
    q = 'DELETE FROM "case" CASCADE'
    # TODO: Find a more SA way to do this

    db.session.execute(q)
    db.session.commit()

    click.echo(f"Done.")


@click.command("export-db")
def export_db_command():
    """
    Export a copy of the database
    """
    raise NotImplementedError


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

    user = new_users[0]
    docket = lookup_docket_by_cl_id(65748821, save=True)
    case = docket_to_case(docket)

    beat = Beat(name="FTX")
    db.session.add(beat)

    db.session.commit()

    beat.curators.append(user)
    beat.cases.append(case)

    db.session.commit()

    ch = Channel(
        service="mastodon",
        account="@bigcases@law.builders",
        account_id="anseljh+bigcases@gmail.com",
    )
    db.session.add(ch)
    db.session.commit()

    beat.channels.append(ch)
    db.session.commit()

    click.echo(f"User: {user}")
    click.echo(f"Beat: {beat}")
    click.echo(f"Case: {case}")
    click.echo(f"Channel: {ch}")
    current_app.logger.debug(f"New users: {new_users}")


@click.command("lookup")
@click.argument("cl-id")
@click.option("--add/--no-add", default=False)
@click.option("--save-json/--no-save-json", default=False)
def lookup_command(cl_id, add, save_json):
    """
    Lookup a case in the RECAP archive by its CourtListener ID,
    and optionally add it.
    """
    result = lookup_docket_by_cl_id(cl_id)
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

    if save_json:
        json_fn = f"output/cl-{cl_id}.json"
        with open(json_fn, "w") as json_f:
            json.dump(result, json_f)
        click.echo(f"Saved {json_fn}.")

    if add:
        click.echo("We'll try to add this case to the DB.")
        add_case(court, docket_number, case_name, cl_id)
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


@click.command("add-case")
def add_command():
    """
    Interactively add a new case
    """
    pass


@click.command("cl-list-subscriptions")
def cl_list_subscriptions_command():
    """
    List CourtListener docket alert subscriptions
    """
    subs = get_docket_alert_subscriptions()
    click.echo("Subscriptions: (CourtListener IDs)")
    click.echo(pformat(subs))


@click.command("cl-subscribe")
@click.argument("cl_id")
def cl_subscribe_command(cl_id: int):
    """
    Add a CourtListener docket alert subscription
    """
    result = subscribe_to_docket_alert(cl_id)
    click.echo(result)


@click.command("list-channels")
def list_channels_command():
    """
    List channels to which BCB2 can post.
    """
    stmt = db.select(Channel)
    click.echo(stmt)
    db_result = db.session.execute(stmt)

    # TODO: Refactor from post_command
    for channel in db_result.scalars():
        textline = f"{channel.id}\t{channel.service} {channel.account} {channel.self_url()}"
        if channel.enabled:
            click.echo(click.style(textline, fg="green"))
        else:
            # Output but greyed out
            click.echo(click.style(textline, fg="magenta"))


@click.command("post")
def post_command():
    """
    Post something manually to one or more channels.
    """
    tab = PrettyTable()
    channel_mapping = {}
    tab.field_names = ["ID", "Service", "Account", "Enabled", "URL"]
    stmt = db.select(Channel)
    db_result = db.session.execute(stmt)
    for channel in db_result.scalars():
        tab.add_row(
            [
                channel.id,
                channel.service,
                channel.account,
                channel.enabled,
                channel.self_url(),
            ]
        )
        channel_mapping[channel.id] = channel
    click.echo(tab)

    channel_input = click.prompt(
        "Which channels? Input ID, comma-separate for multiple, or 'all' for all of them.\n"
    )
    click.echo(channel_input)

    channel_ids = None
    if channel_input == "all":
        # raise NotImplementedError("Don't know how to post to all just yet.")
        channel_ids = list(channel_mapping.keys())
    else:
        channel_ids = list(
            map(int, [s.strip() for s in channel_input.split(",")])
        )
    click.echo(f"Posting to channels: {channel_ids}")

    post_text = click.prompt("What do you want to say?")

    for chid in channel_ids:
        channel = channel_mapping.get(chid)
        if channel is None:
            raise ValueError(f"No channel {chid}")

        if channel.service == "mastodon":

            # TODO: Look up the actual credentials for *this* account and whatnot

            click.echo(f"Let's toot from {channel.account}!")
            click.echo(f"Here's what we're going to say:\n\t{post_text}")
            ready = click.confirm("Ready?")
            if ready:
                m = get_mastodon()
                m.status_post(post_text)
            else:
                click.echo("OK, then!")

        else:
            raise NotImplementedError(f"Not posting to {channel.service} yet")


def init_app(app):
    app.cli.add_command(info_command)
    app.cli.add_command(init_command)
    app.cli.add_command(init_db_command)
    app.cli.add_command(empty_db_command)
    app.cli.add_command(export_db_command)
    app.cli.add_command(bootstrap_dev_data_command)
    app.cli.add_command(lookup_command)
    app.cli.add_command(search_command)
    app.cli.add_command(add_command)
    app.cli.add_command(cl_list_subscriptions_command)
    app.cli.add_command(cl_subscribe_command)
    app.cli.add_command(list_channels_command)
    app.cli.add_command(post_command)
