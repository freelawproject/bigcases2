from django.contrib import admin

from bc.channel.models import Alias

from .models import Sponsorship, Transaction


class AliasInline(admin.TabularInline):
    verbose_name = "Sponsored Alias"
    verbose_name_plural = "Sponsored Aliases"
    model = Alias.sponsorships.through
    extra = 0


@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ("user", "original_amount", "current_amount")
    inlines = (AliasInline,)
    exclude = ("current_amount",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "type", "amount")
