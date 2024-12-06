from django.conf import settings

from bc.core.models import BannerConfig


def banner_settings(request):
    active_banner = BannerConfig.objects.filter(is_active=True).first()
    return {
        "HEADER_BANNER_ENABLED": bool(active_banner),
        "HEADER_BANNER_TITLE": (
            active_banner.banner_title if active_banner else ""
        ),
        "HEADER_BANNER_TEXT": (
            active_banner.banner_text if active_banner else ""
        ),
        "HEADER_BANNER_BUTTON_TEXT": (
            active_banner.banner_button_text if active_banner else ""
        ),
        "HEADER_BANNER_BUTTON_LINK": (
            active_banner.banner_button_link if active_banner else ""
        ),
    }
