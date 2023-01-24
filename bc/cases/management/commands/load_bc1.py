import json

import click
from django.core.management.base import BaseCommand

from bc.cases.models import Docket
from bc.cases.utils.courtlistener import (
    lookup_court,
    trim_docket_ending_number,
)


class Command(BaseCommand):
    help = "Import cases from JSON file into the database"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str)

    def handle(self, *args, **options):
        click.echo("Loading Big Cases Bot v1 JSON file...")

        with open(options["json_file"]) as f:
            bcb1_data = json.load(f)

        for bcb1_record in bcb1_data["cases"]:

            bcb1_court = bcb1_record["court"]
            bcb1_case_number = bcb1_record["case_number"]
            bcb1_name = bcb1_record["name"]

            # Handle erroneous "D. Ore." in original data
            if bcb1_court == "D. Ore.":
                bcb1_court = "D. Or."

            # Handle stray stuff at end of case numbers, e.g., "1:19-cr-00366-1"
            bcb1_case_number = trim_docket_ending_number(bcb1_case_number)

            court_key = lookup_court(bcb1_court[:-1])
            if court_key:
                c = Docket.objects.create(
                    court=court_key,
                    docket_number=bcb1_case_number,
                    bcb1_description=bcb1_name,
                    in_bcb1=True,
                )

        print("Done.")
