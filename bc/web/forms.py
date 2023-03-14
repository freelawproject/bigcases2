from django import forms
from django.forms import ModelForm

from .models import BotSuggestion, WaitList


class BotSuggestionForm(ModelForm):
    TWITTER = "twitter"
    MASTODON = "mastodon"
    PLATFORMS = (
        (TWITTER, "Twitter"),
        (MASTODON, "Mastodon"),
    )
    platform = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        choices=PLATFORMS,
    )

    class Meta:
        model = BotSuggestion
        fields = ("name", "platform", "use_case")

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
    name = forms.CharField(max_length=200)
    company_name = forms.CharField(max_length=200, required=False)

    class Meta:
        model = WaitList
        fields = ("name", "email", "company_name", "platform")

    def clean_platform(self):
        data = self.cleaned_data["platform"]
        return ",".join(data)
