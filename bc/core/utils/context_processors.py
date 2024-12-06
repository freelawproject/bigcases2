from django.conf import settings


def banner_settings(request):
    return {
        "BANNER_ENABLED": settings.BANNER_ENABLED,
    }
