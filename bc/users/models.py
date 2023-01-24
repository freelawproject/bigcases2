from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from bc.core.models import AbstractDateTimeModel

from .managers import CustomUserManager


class User(AbstractDateTimeModel, AbstractBaseUser):
    # Login stuff
    email = models.EmailField(
        help_text="The email address of the user.",
        unique=True,
    )
    affiliation = models.TextField()
    # <-> Channels
    enabled = models.BooleanField(
        help_text=(
            "Overall enable switch. Disable to shut out account entirely."
            "Disabled by default; must enable manually"
        ),
        default=False,
    )
    allow_login = models.BooleanField(
        help_text=(
            "Whether to allow login to the app"
            "Disabled by default; must enable manually"
        ),
        default=False,
    )
    allow_spend = models.BooleanField(
        help_text=(
            "Whether to allow purchasing a docket"
            "Disabled by default; must enable manually"
        ),
        default=False,
    )
    allow_follow = models.BooleanField(
        help_text=(
            "Whether to allow commanding BCB to follow a case"
            "Disabled by default; unless allow_spend is also set"
        ),
        default=False,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
