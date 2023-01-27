from django.core.management.base import BaseCommand

from bc.subscription.utils.courtlistener import subscribe_to_docket_alert


class Command(BaseCommand):
    help = "Add a CourtListener docket alert subscription"

    def add_arguments(self, parser):
        parser.add_argument("cl_id", type=str)

    def handle(self, *args, **options):
        cl_id = options.get("cl_id", None)
        if cl_id:
            result = subscribe_to_docket_alert(cl_id)
