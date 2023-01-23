from django.core.management.base import BaseCommand

from bc.beats.models import Beat
from bc.cases.models import Docket
from bc.channels.models import Channel
from bc.people.models import Judge
from bc.users.models import User


class Command(BaseCommand):
    help = "Delete data from DB but leave structure intact"

    def handle(self, *args, **options):
        print("Emptying database...")

        Docket.objects.all().delete()
        Channel.objects.all().delete()
        Judge.objects.all().delete()
        Beat.objects.all().delete()
        User.objects.all().delete()

        print("Done")
