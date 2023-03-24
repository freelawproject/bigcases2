from django.urls import path
from django.views.generic import TemplateView

from .views import big_cases_about, collaboration, count_dockets, little_cases

urlpatterns = [
    path("", count_dockets, name="homepage"),
    path(
        "big-cases/about/",
        big_cases_about,
        name="big_cases_about",
    ),
    path(
        "big-cases/sponsors/",
        TemplateView.as_view(template_name="big-cases/sponsors.html"),
        name="big_cases_sponsors",
    ),
    path(
        "big-cases/my-code/",
        TemplateView.as_view(template_name="big-cases/my-code.html"),
        name="big_cases_my_code",
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
    path(
        "successful-submission/",
        TemplateView.as_view(template_name="successful-submission.html"),
        name="successful_submission",
    ),
]
