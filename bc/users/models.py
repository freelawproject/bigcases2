from typing import List

from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from bc.core.models import AbstractDateTimeModel

from .managers import CustomUserManager


class User(AbstractDateTimeModel, AbstractBaseUser):
    email = models.EmailField(
        help_text="The email address of the user.",
        unique=True,
    )
    affiliation = models.TextField()
    enabled = models.BooleanField(
        help_text=(
            "Overall enable switch. Disable to shut out account entirely."
            "Disabled by default; must enable manually"
        ),
        default=False,
    )

    REQUIRED_FIELDS: List[str] = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
