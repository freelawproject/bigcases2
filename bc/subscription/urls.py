from django.urls import path

from .api_views import handle_cl_webhook

urlpatterns = [
    path(
        "/webhooks/docket/",
        handle_cl_webhook,
        name="cl_webhook_handler",
    ),
]
