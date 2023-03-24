from django.contrib import admin

from .models import BotSuggestion, WaitList


@admin.register(BotSuggestion)
class BotSuggestionAdmin(admin.ModelAdmin):
    list_display = ("name", "platform", "date_created")


@admin.register(WaitList)
class WaitListAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "company_name",
        "platform",
        "date_created",
    )
