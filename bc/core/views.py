from django.http import HttpRequest, HttpResponse


def sentry_fail(request: HttpRequest) -> HttpResponse:
    division_by_zero = 1 / 0
