from django.urls import path

from .views import sentry_fail

urlpatterns = [
    path("sentry/error/", sentry_fail, name="sentry_fail"),
]
