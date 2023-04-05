from django.urls import path

from .api_views import handle_docket_alert_webhook, handle_recap_fetch_webhook

urlpatterns = [
    path(
        "webhooks/docket/",
        handle_docket_alert_webhook,
        name="docket_alert_webhook_handler",
    ),
    path(
        "webhooks/recap-fetch/",
        handle_recap_fetch_webhook,
        name="recap_fetch_webhook_handler",
    ),
]
