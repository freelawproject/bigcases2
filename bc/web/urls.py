from django.urls import path
from django.views.generic import TemplateView

from .views import collaboration, count_dockets, little_cases, view_docket

urlpatterns = [
    path("", count_dockets, name="homepage"),
    path(
        "big-cases/about/",
        TemplateView.as_view(template_name="big-cases/about.html"),
        name="big_cases_about",
    ),
    path(
        "big-cases/sponsors/",
        TemplateView.as_view(template_name="big-cases/sponsors.html"),
        name="big_cases_sponsors",
    ),
    path(
        "little-cases/",
        little_cases,
        name="little_cases",
    ),
    path(
        "collaboration/",
        collaboration,
        name="collaboration",
    ),
    # Docket pages
    path("docket/<int:subscription_id>/", view_docket, name="docket_details"),
]
