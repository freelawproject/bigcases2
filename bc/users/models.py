from django.contrib.auth.models import AbstractUser
from django.db import models

from bc.core.models import AbstractDateTimeModel


class User(AbstractDateTimeModel, AbstractUser):
    email = models.EmailField(
        help_text="The email address of the user.",
        unique=True,
    )
    activation_key = models.CharField(max_length=64, default="")
    key_expires = models.DateTimeField(
        help_text="The time and date when the user's activation_key expires",
        blank=True,
        null=True,
    )
    email_confirmed = models.BooleanField(
        help_text="The user has confirmed their email address",
        default=False,
    )
    affiliation = models.TextField(help_text="User's affiliations", blank=True)

    @property
    def name(self):
        if self.get_full_name():
            return self.get_full_name()
        return self.username
