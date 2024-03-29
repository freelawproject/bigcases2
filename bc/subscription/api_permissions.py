from django.conf import settings
from rest_framework import exceptions, permissions

from bc.core.utils.network import strip_port_to_make_ip_key


class AllowListPermission(permissions.BasePermission):
    """
    Permission check for trusted IP addresses.
    """

    def has_permission(self, request, view):
        ip_addr = (
            strip_port_to_make_ip_key(group="", request=request)
            or request.META["REMOTE_ADDR"]
        )

        if settings.DEVELOPMENT:
            return True
        if ip_addr not in settings.COURTLISTENER_ALLOW_IPS:
            raise exceptions.PermissionDenied("Ip not allowed")
        return True
