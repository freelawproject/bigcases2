from django.urls import path
from django.views.generic import TemplateView

from .api_views import handle_docket_alert_webhook, handle_recap_fetch_webhook
from .views import search

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
    path("search-case/", search, name="search_cases"),
    path(
        "add-cases/",
        TemplateView.as_view(template_name="add-case.html"),
        name="add_cases",
    ),
]
