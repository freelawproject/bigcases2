from django.urls import path

from .api_views import receive_mastodon_push

urlpatterns = [
    path(
        "/webhooks/mastodon",
        receive_mastodon_push,
        name="mastodon_push_handler",
    ),
]
