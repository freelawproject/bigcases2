from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from bc.core.utils.network import ratelimiter_unsafe_5_per_30m

from .views import (
    big_cases_about,
    big_cases_sponsors,
    collaboration,
    count_dockets,
    little_cases,
    little_cases_details,
    little_cases_suggest_form,
)

urlpatterns = [
    path("", count_dockets, name="homepage"),
    path(
        "sponsors/",
        RedirectView.as_view(
            pattern_name="big_cases_sponsors", permanent=True
        ),
    ),
    path(
        "big-cases/about/",
        big_cases_about,
        name="big_cases_about",
    ),
    path(
        "big-cases/sponsors/",
        big_cases_sponsors,
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
        "little-cases/suggest-a-bot/",
        ratelimiter_unsafe_5_per_30m(little_cases_suggest_form),
        name="little_cases_suggest_bot",
    ),
    path(
        "little-cases/<slug:slug>/",
        little_cases_details,
        name="little_cases_detail",
    ),
    path(
        "collaboration/",
        ratelimiter_unsafe_5_per_30m(collaboration),
        name="collaboration",
    ),
    path(
        "successful-submission/",
        TemplateView.as_view(template_name="successful-submission.html"),
        name="successful_submission",
    ),
]
