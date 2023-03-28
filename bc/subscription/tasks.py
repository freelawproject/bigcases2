import requests
from django.db import transaction

from bc.channel.models import Post
from bc.channel.selectors import get_enabled_channels
from bc.core.utils.microservices import get_thumbnails_from_range
from bc.core.utils.status.selectors import get_template_for_channel
from bc.core.utils.status.templates import DO_NOT_POST
from bc.subscription.utils.courtlistener import lookup_document_by_doc_id

from .models import FilingWebhookEvent, Subscription


@transaction.atomic
def process_filing_webhook_event(fwe_pk) -> FilingWebhookEvent:
    """Process an event from a CL webhook.

    :param fwe_pk: The PK of the item you want to work on.
    :return: A FilingWebhookEvent object that was updated.
    """
    filing_webhook_event = FilingWebhookEvent.objects.get(pk=fwe_pk)

    if not filing_webhook_event.docket_id:
        return filing_webhook_event

    try:
        with transaction.atomic():
            subscription = Subscription.objects.get(
                cl_docket_id=filing_webhook_event.docket_id
            )
    except Subscription.DoesNotExist:
        # We don't know why we got this webhook event. Ignore it.
        filing_webhook_event.status = FilingWebhookEvent.FAILED
        filing_webhook_event.save()
        return filing_webhook_event

    filing_webhook_event.status = FilingWebhookEvent.SUCCESSFUL
    filing_webhook_event.subscription = subscription
    filing_webhook_event.save()

    if DO_NOT_POST.search(filing_webhook_event.description):
        return filing_webhook_event

    cl_document = lookup_document_by_doc_id(filing_webhook_event.cl_doc_id)
    document_url = (
        f"https://storage.courtlistener.com/{cl_document['filepath_local']}"
        if cl_document["filepath_local"]
        else None
    )

    document = None
    if document_url:
        document_request = requests.get(document_url, timeout=60)
        document_request.raise_for_status()
        document = document_request.content

    for channel in get_enabled_channels():
        template = get_template_for_channel(
            channel.service, filing_webhook_event.document_number
        )

        message, image = template.format(
            docket=subscription.name_with_summary,
            description=filing_webhook_event.description,
            doc_num=filing_webhook_event.document_number,
            pdf_link=filing_webhook_event.cl_pdf_or_pacer_url,
            docket_link=filing_webhook_event.cl_docket_url,
        )

        files = None
        if document:
            thumbnail_range = "[1,2,3]" if image else "[1,2,3,4]"
            files = get_thumbnails_from_range(document, thumbnail_range)

        api = channel.get_api_wrapper()
        api_post_id = api.add_status(message, image, files)

        Post.objects.create(
            filing_webhook_event=filing_webhook_event,
            channel=channel,
            object_id=api_post_id,
            text=message,
        )

    return filing_webhook_event
