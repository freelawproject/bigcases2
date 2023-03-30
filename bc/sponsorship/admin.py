from django.contrib import admin

from .models import Sponsorship, Transaction


@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ("user", "original_amount", "current_amount")
    exclude = ("current_amount",)


admin.site.register(Transaction)
