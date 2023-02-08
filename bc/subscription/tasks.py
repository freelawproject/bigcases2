from .models import FilingWebhookEvent, Subscription


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
    except Subscription.DoesNotExist:
        filing_webhook_event.status = FilingWebhookEvent.FAILED
        filing_webhook_event.save()

    return filing_webhook_event
