from typing import NotRequired, TypedDict

from django.http import HttpRequest

from bc.users.models import User


class AuthenticatedHttpRequest(HttpRequest):
    user: User


class EmailType(TypedDict):
    subject: str
    body: str
    from_email: str
    to: NotRequired[list[str]]


class MessageType(TypedDict):
    level: int
    message: str
