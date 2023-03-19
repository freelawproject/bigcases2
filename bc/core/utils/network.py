from django.http import HttpRequest
from django_ratelimit.core import get_header
from django_ratelimit.decorators import ratelimit


def strip_port_to_make_ip_key(group: str, request: HttpRequest) -> str:
    """Make a good key to use for caching the request's IP

    CloudFront provides a header that returns the user's IP and port,
    so we need to strip it to make the user's IP  a consistent key.

    So we go from something like:

        96.23.39.106:51396

    To:

        96.23.39.106

    :param group: Unused: The group key from the ratelimiter
    :param request: The HTTP request from the user
    :return: A simple key that can be used to throttle the user if needed.
    """
    header = get_header(request, "CloudFront-Viewer-Address")
    return header.split(":")[0]


ratelimiter_unsafe_10_per_m = ratelimit(
    key=strip_port_to_make_ip_key,
    rate="10/m",
    method=ratelimit.UNSAFE,
    block=True,
)
