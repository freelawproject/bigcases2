from django.core.management.base import BaseCommand

from bc.subscription.services import create_subscription_from_docket
from bc.subscription.utils.courtlistener import (
    lookup_docket_by_cl_id,
    subscribe_to_docket_alert,
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
            help="Save and Subscribe to the case found using the CL API",
        )

    def handle(self, *args, **options):
        result = lookup_docket_by_cl_id(options["cl-id"])
        if result:
            court = result["court_id"]
            case_name = result["case_name"]
            docket_number = result["docket_number"]
            uri = result["absolute_url"]
            cl_url = f"https://www.courtlistener.com{uri}"
            self.stdout.write(self.style.SUCCESS(f"Name: {case_name}"))
            self.stdout.write(self.style.SUCCESS(f"Case no.: {docket_number}"))
            self.stdout.write(self.style.SUCCESS(f"Court: {court}"))
            self.stdout.write(self.style.SUCCESS(f"Link: {cl_url}"))

            if options["add"]:
                self.stdout.write(
                    self.style.WARNING("We'll try to add this case to the DB.")
                )
                create_subscription_from_docket(result)
                self.stdout.write(self.style.SUCCESS("Added!"))

                cl_subscription = subscribe_to_docket_alert(options["cl-id"])
                if cl_subscription:
                    self.stdout.write(self.style.SUCCESS("Subscribed!"))
        else:
            self.stdout.write(self.style.ERROR("Case not found"))
