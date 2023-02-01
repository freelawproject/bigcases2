from django.urls import path

from .views import health_check, sentry_fail

urlpatterns = [
    path("monitoring/health-check/", health_check, name="health_check"),
    path("sentry/error/", sentry_fail, name="sentry_fail"),
]
