from django.contrib.auth.models import AbstractUser
from django.db import models

from bc.core.models import AbstractDateTimeModel


class User(AbstractDateTimeModel, AbstractUser):
    email = models.EmailField(
        help_text="The email address of the user.",
        unique=True,
    )
    affiliation = models.TextField()
