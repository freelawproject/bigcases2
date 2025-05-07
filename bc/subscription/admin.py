from django.contrib import admin

from .models import FilingWebhookEvent, Subscription


class ChannelInline(admin.StackedInline):
    model = Subscription.channel.through
    extra = 0


class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [
        ChannelInline,
    ]
    exclude = ["channel"]
    search_fields = (
        "cl_docket_id",
        "pacer_case_id",
        "channel__group__name",
    )
    list_filter = ("channel__group",)


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(FilingWebhookEvent)
