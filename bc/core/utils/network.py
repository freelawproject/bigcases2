from django.http import HttpRequest
from django_ratelimit.core import get_header


def strip_port_to_make_ip_key(group: str, request: HttpRequest) -> str | None:
    """Make a good key to use for caching the request's IP

    CloudFront provides a header that returns the user's IP and port,
    so we need to strip it to make the user's IP  a consistent key.

    So we go from something like:

        96.23.39.106:51396

    To:

        96.23.39.106

    :param ip_str: the IP address of the viewer and the source port of the request
    :return: A simple key that can be used to throttle the user if needed.
    """
    header = get_header(request, "CloudFront-Viewer-Address")
    return header.split(":")[0]
