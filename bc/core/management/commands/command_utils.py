# This file is a slightly modified copy from CourtListener

import logging

from django.core.management import BaseCommand


class VerboseCommand(BaseCommand):
    """Add logging based on the verbosity argument."""

    logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        verbosity = options.get("verbosity")
        if not verbosity or verbosity == 0:
            self.logger.setLevel(logging.WARN)
        elif verbosity == 1:  # default
            self.logger.setLevel(logging.INFO)
        elif verbosity > 1:
            self.logger.setLevel(logging.DEBUG)
