from bc.channel.models import Channel
from bc.core.utils.status.base import BaseTemplate

from .templates import (
    BLUESKY_FOLLOW_A_NEW_CASE,
    BLUESKY_MINUTE_TEMPLATE,
    BLUESKY_POST_TEMPLATE,
    MASTODON_FOLLOW_A_NEW_CASE,
    MASTODON_MINUTE_TEMPLATE,
    MASTODON_POST_TEMPLATE,
    TWITTER_FOLLOW_A_NEW_CASE,
    TWITTER_MINUTE_TEMPLATE,
    TWITTER_POST_TEMPLATE,
    BlueskyTemplate,
    MastodonTemplate,
    TwitterTemplate,
)


def get_template_for_channel(
    service: int, document_number: int | None
) -> TwitterTemplate | MastodonTemplate | BlueskyTemplate:
    """Returns a template object that uses the data of a webhook to
    create a new status update in the given service. This method
    checks the document number to pick one of the templates available.

    Args:
        service (int): the service identifier.
        document_number (int | None): the document number of the webhook
            event.

    Returns:
        TwitterTemplate | MastodonTemplate | BlueskyTemplate: template object to create
            a new post.
    """
    match service:
        case Channel.TWITTER:
            return (
                TWITTER_POST_TEMPLATE
                if document_number
                else TWITTER_MINUTE_TEMPLATE
            )
        case Channel.MASTODON:
            return (
                MASTODON_POST_TEMPLATE
                if document_number
                else MASTODON_MINUTE_TEMPLATE
            )
        case Channel.BLUESKY:
            return (
                BLUESKY_POST_TEMPLATE
                if document_number
                else BLUESKY_MINUTE_TEMPLATE
            )
        case _:
            raise NotImplementedError(
                f"No wrapper implemented for service: '{service}'."
            )


def get_new_case_template(service: int) -> BaseTemplate:
    """Returns a template object that uses the data of a subscription
    to create a status update in the given service. this method
    checks the article URL to pick one of the templates available.

    Args:
        service (int): the service identifier

    Returns:
        BaseTemplate: template object to create a new post
    """

    new_case_templates: dict[int, BaseTemplate] = {
        Channel.BLUESKY: BLUESKY_FOLLOW_A_NEW_CASE,
        Channel.MASTODON: MASTODON_FOLLOW_A_NEW_CASE,
        Channel.TWITTER: TWITTER_FOLLOW_A_NEW_CASE,
    }

    if service in new_case_templates:
        return new_case_templates[service]

    raise NotImplementedError(
        f"No template implemented for service: '{service}'."
    )
