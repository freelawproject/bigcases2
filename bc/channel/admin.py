from django import forms
from django.contrib import admin
from django.forms.widgets import TextInput

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


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "__all__"
        widgets = {
            "border_color": TextInput(attrs={"type": "color"}),
        }


class GroupAdmin(admin.ModelAdmin):
    inlines = (ChannelInline,)
    exclude = ["sponsorships"]
    prepopulated_fields = {"slug": ["name"]}
    form = GroupAdminForm


admin.site.register(Channel, ChannelAdmin)
admin.site.register(Group, GroupAdmin)
