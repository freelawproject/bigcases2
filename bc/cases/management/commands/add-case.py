from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Interactively add a new case"

    def handle(self, *args, **options):
        raise NotImplementedError
