from django.contrib import admin

from bc.core.models import BannerConfig


@admin.register(BannerConfig)
class BannerConfigAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_active", "title", "text")
    list_filter = ("is_active",)
    search_fields = (
        "title",
        "text",
        "button_text",
        "button_link",
    )
