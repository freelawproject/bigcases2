from django import forms
from django.forms import ModelForm

from .models import Subscription


class AddSubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ("docket_name", "case_summary", "article_url")
        labels = {
            "docket_name": "Name",
            "case_summary": "Case Summary",
            "article_url": "Article URL",
        }
        help_texts = {
            "docket_name": "Name of the case. Use this input to tweak the name in case it's really long.",
        }
        widgets = {
            "docket_name": forms.TextInput(),
        }
