from django.contrib import admin

from bc.channel.models import Channel

from .models import Subscription


class ChannelInline(admin.StackedInline):
    model = Subscription.channel.through
    extra = 0


class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [
        ChannelInline,
    ]
    exclude = ["channel"]


admin.site.register(Subscription, SubscriptionAdmin)
