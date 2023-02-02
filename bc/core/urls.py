from django.urls import path

from .views import health_check, rq_fail, sentry_fail

urlpatterns = [
    path("monitoring/health-check/", health_check, name="health_check"),
    path("sentry/error/", sentry_fail, name="sentry_fail"),
    path("sentry/rq-fail/", rq_fail, name="rq_fail"),
]
