from django.urls import path

from .api_views import handle_docket_alert_webhook, handle_recap_fetch_webhook
from .views import AddCaseView, search

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
        AddCaseView.as_view(),
        name="add_cases",
    ),
]
