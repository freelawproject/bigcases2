from django.urls import path

from .views import count_dockets, view_docket

urlpatterns = [
    path("", count_dockets, name="homepage"),
    # Docket pages
    path("docket/<int:subscription_id>/", view_docket, name="docket_details"),
]
