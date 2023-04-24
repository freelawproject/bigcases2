from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response

from .utils.courtlistener import get_cl_id_from_query, lookup_docket_by_cl_id


def search(request: Request) -> Response:
    query = request.GET.get("q")

    context = {"query": query}

    try:
        docket_id = get_cl_id_from_query(query)
        data = lookup_docket_by_cl_id(int(docket_id))
        if data:
            context["docket_id"] = docket_id
            context["case_name"] = data["case_name"]
            template = "./includes/search_htmx/case-form.html"
        else:
            template = "./includes/search_htmx/no-result.html"
    except ValidationError:
        template = "./includes/search_htmx/invalid-keyword.html"

    return render(request, template, context)
