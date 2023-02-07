from django.conf import settings
from rest_framework import exceptions, permissions


class WhitelistPermission(permissions.BasePermission):
    """
    Permission check for whitelisted IP.
    """

    def has_permission(self, request, view):
        ip_addr = request.META["REMOTE_ADDR"]
        if settings.DEVELOPMENT:
            return True
        if ip_addr not in settings.COURTLISTENER_ALLOW_IPS:
            raise exceptions.PermissionDenied('Ip not allowed')
