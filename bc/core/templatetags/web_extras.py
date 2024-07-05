from django import template
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


@register.simple_tag(takes_context=True)
def get_full_host(context):
    """Return the current URL with the correct protocol and port.

    No trailing slash.

    :param context: The template context that is passed in.
    :type context: RequestContext
    """
    r = context.get("request")
    if r is None:
        protocol = "http"
        domain_and_port = "bots.law"
    else:
        protocol = "https" if r.is_secure() else "http"
        domain_and_port = r.get_host()

    return mark_safe(
        "{protocol}://{domain_and_port}".format(
            protocol=protocol,
            domain_and_port=domain_and_port,
        )
    )
