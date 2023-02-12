from bc.channel.models import Channel
from bc.channel.utils.masto import post_status
from bc.core.utils.messages import NEW_FILING_TEMPLATE

from .models import FilingWebhookEvent, Post, Subscription


def process_filing_webhook_event(fwe_pk) -> FilingWebhookEvent:
    """Process an event from a CL webhook.

    :param fwe_pk: The PK of the item you want to work on.
    :return: A FilingWebhookEvent object that was updated.
    """
    filing_webhook_event = FilingWebhookEvent.objects.get(pk=fwe_pk)
    try:
        if filing_webhook_event.docket_id:
            subscription = Subscription.objects.get(
                cl_docket_id=filing_webhook_event.docket_id
            )
            filing_webhook_event.subscription = subscription
            filing_webhook_event.save()

            message = NEW_FILING_TEMPLATE.format(
                docket=subscription.docket_name,
                desc=filing_webhook_event.description,
                link=filing_webhook_event.document_link(),
            )

            api_post_id = post_status(message)

            channel = Channel.objects.get(service=Channel.MASTODON)
            Post.objects.create(
                filing_webhook_event=filing_webhook_event,
                channel=channel,
                object_id=api_post_id,
            )

    except Subscription.DoesNotExist:
        filing_webhook_event.status = FilingWebhookEvent.FAILED
        filing_webhook_event.save()

    return filing_webhook_event
