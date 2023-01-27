import logging

from django.http import HttpRequest, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .utils.masto import get_keys, get_mastodon

logger = logging.getLogger(__name__)


@api_view(["POST"])
def receive_mastodon_push(request: HttpRequest) -> HttpResponse:
    logger.debug("Received a push webhook from Mastodon.")
    logger.debug(f"Request: {request}")
    logger.debug(f"Request headers: {request.headers}")
    logger.debug(f"Request data: {request.data}")

    m = get_mastodon()
    priv_dict, _ = get_keys()
    push = m.push_subscription_decrypt_push(
        data=request.data,
        decrypt_params=priv_dict,
        encryption_header=request.headers.get("Encryption"),
        crypto_key_header=request.headers.get("Crypto-Key"),
    )
    logger.debug(f"push: {push}")

    return Response(status=status.HTTP_200_OK)
