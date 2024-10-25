from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse


def threads_callback(request: HttpRequest) -> HttpResponse:
    code = request.GET.get("code", "No code found")

    return TemplateResponse(
        request, "threads_code.html", {"code": code}
    )
