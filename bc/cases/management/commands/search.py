import click
from django.core.management.base import BaseCommand

from bc.cases.utils.courtlistener import add_case, get_case_from_cl


class Command(BaseCommand):
    help = "Search for a case in CourtListener, and optionally add it to the database."

    def add_arguments(self, parser):
        parser.add_argument("court", type=str)
        parser.add_argument("case_number", type=str)
        parser.add_argument(
            "--add",
            action="store_true",
            help="Store case found",
        )

    def handle(self, *args, **options):
        click.echo("cli.search() called")
        court = options["court"]
        case_number = options["case_number"]
        add = options["add"]
        cl_result = get_case_from_cl(court, case_number)
        if cl_result:
            print(
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
