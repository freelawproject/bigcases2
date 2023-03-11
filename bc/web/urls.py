from django.urls import path
from django.views.generic import TemplateView

from .views import count_dockets, view_docket

urlpatterns = [
    path("", count_dockets, name="homepage"),
    path(
        "big-cases/about/",
        TemplateView.as_view(template_name="big_cases/about.html"),
        name="big_cases_about",
    ),
    path(
        "big-cases/sponsors/",
        TemplateView.as_view(template_name="big_cases/sponsors.html"),
        name="big_cases_sponsors",
    ),
    # Docket pages
    path("docket/<int:subscription_id>/", view_docket, name="docket_details"),
]
