from django.contrib.auth.models import AbstractUser
from django.core.signing import TimestampSigner
from django.db import models

from bc.core.models import AbstractDateTimeModel


class User(AbstractDateTimeModel, AbstractUser):
    email = models.EmailField(
        help_text="The email address of the user.",
        unique=True,
    )
    email_confirmed = models.BooleanField(
        help_text="The user has confirmed their email address",
        default=False,
    )
    affiliation = models.TextField(help_text="User's affiliations", blank=True)

    signer = TimestampSigner(sep="/", salt="user.Users")

    def get_signed_pk(self):
        return self.signer.sign(self.pk)

    @property
    def name(self):
        if self.get_full_name():
            return self.get_full_name()
        return self.username
