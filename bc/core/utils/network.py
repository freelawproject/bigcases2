from typing import Optional


def strip_port_to_make_ip_key(ip_str: str | None) -> str | None:
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
    if ip_str:
        return ip_str.split(":")[0]
    return None
