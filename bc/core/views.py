from http import HTTPStatus

from django.http import HttpRequest, HttpResponse, JsonResponse

from .utils import check_postgresql


def sentry_fail(request: HttpRequest) -> HttpResponse:
    division_by_zero = 1 / 0
    return HttpResponse(division_by_zero)


def health_check(request: HttpRequest) -> JsonResponse:
    """Check if we can connect to various services."""

    is_postgresql_up = check_postgresql()

    status = HTTPStatus.OK
    if not is_postgresql_up:
        status = HTTPStatus.INTERNAL_SERVER_ERROR

    return JsonResponse(
        {
            "is_postgresql_up": is_postgresql_up,
        },
        status=status,
    )
