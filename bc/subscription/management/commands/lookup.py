from django.core.management.base import BaseCommand

from bc.subscription.utils.courtlistener import (
    add_case,
    lookup_docket_by_cl_id,
)


class Command(BaseCommand):
    help = (
        "Lookup a case in the RECAP archive by its CourtListener ID, "
        "optionally add it."
    )

    def add_arguments(self, parser):
        parser.add_argument("cl-id", type=str)
        parser.add_argument(
            "--add",
            action="store_true",
            help="Store case found",
        )

    def handle(self, *args, **options):
        result = lookup_docket_by_cl_id(options["cl-id"])
        court_url = result["court"]
        court = court_url_to_key(court_url)
        case_name = result["case_name"]
        docket_number = result["docket_number"]
        uri = result["absolute_url"]
        cl_url = f"https://www.courtlistener.com{uri}"
        self.stdout.write(self.style.SUCCESS(f"Name: {case_name}"))
        self.stdout.write(self.style.SUCCESS(f"Case no.: {docket_number}"))
        self.stdout.write(self.style.SUCCESS(f"Court: {court}"))
        self.stdout.write(self.style.SUCCESS(f"Link: {cl_url}"))

        if options["add"]:
            self.stdout.write(self.style.NOTICE("We'll try to add this case to the DB."))
            add_case(court, docket_number, case_name, options["cl-id"])
            self.stdout.write(self.style.SUCCESS("Added!"))
