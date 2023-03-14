from django.db import models

from bc.core.models import AbstractDateTimeModel


class BotSuggestion(AbstractDateTimeModel):
    name = models.CharField(
        help_text="Name of the user making the suggestion",
        max_length=100,
    )
    platform = models.TextField(
        help_text="List of platforms where the bot would work"
    )
    use_case = models.TextField(
        help_text="Description of bot and the kinds of cases it would follow."
    )


class WaitList(AbstractDateTimeModel):
    platform = models.TextField(
        help_text="List of platforms to include features of the bots"
    )
    name = models.CharField(
        help_text="Name of the user submitting the form",
        max_length=100,
    )
    email = models.EmailField(
        help_text="Email of the user submitting the form",
    )
    company_name = models.TextField(blank=True)
