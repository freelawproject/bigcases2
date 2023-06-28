from django.db import models

from bc.core.models import AbstractDateTimeModel


class BotSuggestion(AbstractDateTimeModel):
    bot_name = models.CharField(
        help_text="Name of the user making the suggestion",
        max_length=100,
    )
    platform = models.CharField(
        help_text="List of platforms where the bot would work",
        max_length=100,
    )
    purpose = models.TextField(
        help_text="Description of bot and the kinds of cases it would follow."
    )
    user_full_name = models.CharField(
        help_text="The full name of the user", default="", max_length=150
    )
    user_email = models.EmailField(
        help_text="The email address of the user", default=""
    )
    user_expertise = models.TextField(
        help_text="Description of the user's skills or knowledge in the field",
        default="",
    )
    is_curator = models.BooleanField(
        help_text="whether the user would want to curate the bot or not",
        default=True,
    )
    suggested_curators = models.CharField(
        help_text="Users suggested for bot curation",
        max_length=100,
        default="",
        blank=True,
    )


class WaitList(AbstractDateTimeModel):
    platform = models.CharField(
        help_text="List of platforms to include features of the bots",
        max_length=100,
    )
    name = models.CharField(
        help_text="Name of the user submitting the form",
        max_length=100,
    )
    email = models.EmailField(
        help_text="Email of the user submitting the form",
    )
    company_name = models.CharField(max_length=100, blank=True)
