import logging
from http import HTTPStatus

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .utils.connectors.masto import MastodonConnector

logger = logging.getLogger(__name__)


@api_view(["POST"])
def receive_mastodon_push(request: Request) -> Response:
    logger.debug("Received a push webhook from Mastodon.")
    logger.debug(f"Request: {request}")
    logger.debug(f"Request headers: {request.headers}")
    logger.debug(f"Request data: {request.data}")

    m = MastodonConnector()  # type: ignore
    priv_dict, _ = m.get_keys()
    push = m.api.push_subscription_decrypt_push(
        data=request.data,
        decrypt_params=priv_dict,
        encryption_header=request.headers.get("Encryption"),
        crypto_key_header=request.headers.get("Crypto-Key"),
    )
    logger.debug(f"push: {push}")

    return Response(status=HTTPStatus.OK)
