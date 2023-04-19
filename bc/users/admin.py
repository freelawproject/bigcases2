from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (  # type: ignore
        # Custom fields added on to the bottom
        ("Extra Fields", {"fields": ["affiliation"]}),
    )
    add_fieldsets = (
        (None, {"classes": ["wide"], "fields": ["email"]}),
    ) + BaseUserAdmin.add_fieldsets


admin.site.register(User, UserAdmin)
