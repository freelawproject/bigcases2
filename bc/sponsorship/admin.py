from django.contrib import admin

from bc.channel.models import Group

from .models import Sponsorship, Transaction


class GroupsInline(admin.TabularInline):
    verbose_name = "Sponsored Group"
    verbose_name_plural = "Sponsored Groups"
    model = Group.sponsorships.through
    extra = 0


@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ("user", "original_amount", "current_amount")
    inlines = (GroupsInline,)
    exclude = ("current_amount",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "type", "amount")
