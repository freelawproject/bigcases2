from http import HTTPStatus

from django.http import HttpRequest, HttpResponse, JsonResponse

from .tasks import fail_task
from .utils.connections import check_postgresql, check_redis


def sentry_fail(request: HttpRequest) -> HttpResponse:
    division_by_zero = 1 / 0
    return HttpResponse(division_by_zero)


def health_check(request: HttpRequest) -> JsonResponse:
    """Check if we can connect to various services."""
    is_redis_up = check_redis()
    is_postgresql_up = check_postgresql()

    status = HTTPStatus.OK
    if not all([is_postgresql_up, is_redis_up]):
        status = HTTPStatus.INTERNAL_SERVER_ERROR

    return JsonResponse(
        {
            "is_redis_up": is_redis_up,
            "is_postgresql_up": is_postgresql_up,
        },
        status=status,
    )


def rq_fail(request: HttpRequest) -> HttpResponse:
    fail_task.delay()
    return HttpResponse("Successfully failed RQ.")
