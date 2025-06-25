from django import forms
from django.forms import ModelForm

from .models import BotSuggestion, WaitList


class BotSuggestionForm(ModelForm):
    BLUESKY = "bluesky"
    MASTODON = "mastodon"
    PLATFORMS = (
        (BLUESKY, "Bluesky"),
        (MASTODON, "Mastodon"),
    )
    BOOLEAN_CHOICES = ((True, "Yes"), (False, "No"))
    platform = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        choices=PLATFORMS,
    )
    is_curator = forms.ChoiceField(
        widget=forms.Select(),
        choices=BOOLEAN_CHOICES,
        label="Would you want to curate the bot?",
    )

    class Meta:
        model = BotSuggestion
        fields = (
            "bot_name",
            "platform",
            "purpose",
            "user_full_name",
            "user_email",
            "user_expertise",
            "is_curator",
            "suggested_curators",
        )
        labels = {
            "purpose": "Purpose of the bot",
            "user_full_name": "Your full name",
            "user_email": "Your email address",
            "user_expertise": "Your expertise in this field",
            "suggested_curators": "Who would you recommend?",
        }
        widgets = {
            "purpose": forms.Textarea(attrs={"rows": 4}),
            "user_expertise": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_platform(self):
        data = self.cleaned_data["platform"]
        return ",".join(data)


class WaitListForm(ModelForm):
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    GCHAT = "google chat"
    PLATFORMS = (
        (SLACK, "Slack"),
        (DISCORD, "Discord"),
        (TEAMS, "Teams"),
        (GCHAT, "Google Chat"),
    )
    platform = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        choices=PLATFORMS,
    )
    company_name = forms.CharField(required=False)

    class Meta:
        model = WaitList
        fields = ("name", "email", "company_name", "platform")

    def clean_platform(self):
        data = self.cleaned_data["platform"]
        return ",".join(data)
