from django.db import models

from bc.cases.models import Docket
from bc.channels.models import Channel
from bc.core.models import AbstractDateTimeModel
from bc.users.models import User


class Beat(AbstractDateTimeModel):
    name = models.CharField(max_length=100)
    docket = models.ManyToManyField(
        Docket,
        help_text="Foreign key as a relation to the Docket object.",
        related_name="beats",
    )
    curators = models.ManyToManyField(
        User,
        help_text="Foreign key as a relation to the User object.",
        related_name="beats",
    )
    channels = models.ManyToManyField(
        Channel,
        help_text="Foreign key as a relation to the Channel object.",
        related_name="beats",
    )
