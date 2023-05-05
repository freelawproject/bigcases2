from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from bc.channel.models import Channel

from .models import User


class UserChannelInline(admin.TabularInline):
    model = Channel.user.through
    extra = 0


class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (  # type: ignore
        # Custom fields added on to the bottom
        ("Extra Fields", {"fields": ["affiliation"]}),
    )
    add_fieldsets = (
        (None, {"classes": ["wide"], "fields": ["email"]}),
    ) + BaseUserAdmin.add_fieldsets

    inlines = (UserChannelInline,)


admin.site.register(User, UserAdmin)
