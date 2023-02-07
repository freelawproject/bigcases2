from .models import FilingUpdate, Subscription


def process_filing_update(pk):
    """Process an event from a CL webhook.

    :param pk: The PK of the item you want to work on.
    :return: A FilingUpdate object that was updated.
    """
    filing_update = FilingUpdate.objects.get(pk=pk)
    try:
        if filing_update.docket_id:
            subscription = Subscription.objects.get(
                cl_docket_id=filing_update.docket_id
            )
            filing_update.subscription = subscription
            filing_update.save()
    except Subscription.DoesNotExist:
        filing_update.status = FilingUpdate.FAILED
        filing_update.save()

    return filing_update
