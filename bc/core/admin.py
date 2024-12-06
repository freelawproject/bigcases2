from django.contrib import admin

from bc.core.models import BannerConfig


@admin.register(BannerConfig)
class BannerConfigAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_active", "banner_title", "banner_text")
    list_filter = ("is_active",)
    search_fields = (
        "banner_title",
        "banner_text",
        "banner_button_text",
        "banner_button_link",
    )
