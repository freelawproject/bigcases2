from django.contrib import admin

from .models import Sponsorship, Transaction


@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ("user", "original_amount", "current_amount")
    exclude = ("current_amount",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "type", "amount")
