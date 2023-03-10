from django.urls import path

from .views import about, count_dockets, sponsor, view_docket

urlpatterns = [
    path("", count_dockets, name="homepage"),
    path("big-cases/about/", about, name="about"),
    path("big-cases/sponsors/", sponsor, name="sponsors"),
    # Docket pages
    path("docket/<int:subscription_id>/", view_docket, name="docket_details"),
]
