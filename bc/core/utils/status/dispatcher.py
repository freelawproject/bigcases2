from bc.channel.models import Channel

from .templates import (
    MASTODON_MINUTE_TEMPLATE,
    MASTODON_POST_TEMPLATE,
    TWITTER_MINUTE_TEMPLATE,
    TWITTER_POST_TEMPLATE,
)


def post_template_dispatcher(service, document_number):
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
        case _:
            raise NotImplementedError(
                f"No wrapper implemented for service: '{service}'."
            )
