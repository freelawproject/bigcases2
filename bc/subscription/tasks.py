from bc.channel.models import Post
from bc.channel.selectors import get_mastodon_channel
from bc.channel.utils.masto import post_status as mastodon_post
from bc.core.utils.messages import MASTODON_POST_TEMPLATE

from .models import FilingWebhookEvent, Subscription


def process_filing_webhook_event(fwe_pk) -> FilingWebhookEvent:
    """Process an event from a CL webhook.

    :param fwe_pk: The PK of the item you want to work on.
    :return: A FilingWebhookEvent object that was updated.
    """
    filing_webhook_event = FilingWebhookEvent.objects.get(pk=fwe_pk)
    if filing_webhook_event.docket_id:
        try:
            subscription = Subscription.objects.get(
                cl_docket_id=filing_webhook_event.docket_id
            )
        except Subscription.DoesNotExist:
            # We don't know why we got this webhook event. Ignore it.
            filing_webhook_event.status = FilingWebhookEvent.FAILED
            filing_webhook_event.save()
            return filing_webhook_event

        filing_webhook_event.subscription = subscription
        filing_webhook_event.save()

        message = MASTODON_POST_TEMPLATE.format(
            docket=subscription.docket_name,
            desc=filing_webhook_event.description,
            pdf_link=filing_webhook_event.cl_pdf_or_pacer_url,
            docket_link=filing_webhook_event.cl_docket_url,
        )

        api_post_id = mastodon_post(message)

        channel = get_mastodon_channel()
        Post.objects.create(
            filing_webhook_event=filing_webhook_event,
            channel=channel,
            object_id=api_post_id,
            text=message,
        )

    return filing_webhook_event
