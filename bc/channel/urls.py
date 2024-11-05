from django.urls import path

from .api_views import receive_mastodon_push
from .views import threads_callback

urlpatterns = [
    path(
        "webhooks/mastodon/",
        receive_mastodon_push,
        name="mastodon_push_handler",
    ),
    path(
        "threads_callback/",
        threads_callback,
        name="threads_code_display",
    ),
]
