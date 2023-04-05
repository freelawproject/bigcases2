from http import HTTPStatus

from rest_framework.exceptions import APIException


class BadRequest(APIException):
    status_code = HTTPStatus.BAD_REQUEST
    default_code = "bad_request"


class IdempotencyKeyMissing(BadRequest):
    default_detail = (
        "Idempotency key is required and was not specified in the header"
    )


class WebhookNotSupported(BadRequest):
    default_detail = "Webhook type not supported"


class DocumentFetchFailure(BadRequest):
    def __init__(self, detail=None):
        self.detail = detail
