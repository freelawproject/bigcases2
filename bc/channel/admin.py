from django.contrib import admin

from .models import Channel, Group


class UserInline(admin.StackedInline):
    verbose_name = "Curator"
    verbose_name_plural = "Curators"
    model = Channel.user.through
    extra = 0


class ChannelAdmin(admin.ModelAdmin):
    inlines = [
        UserInline,
    ]
    exclude = ["user"]


class ChannelInline(admin.TabularInline):
    model = Channel
    extra = 0
    fields = ["service", "account", "account_id", "enabled"]

    def has_add_permission(self, request, obj):
        return False


class GroupAdmin(admin.ModelAdmin):
    inlines = (ChannelInline,)
    exclude = ["sponsorships"]


admin.site.register(Channel, ChannelAdmin)
admin.site.register(Group, GroupAdmin)
