from bc.subscription.models import FilingWebhookEvent

from .models import Sponsorship, Transaction


def log_purchase(
    sponsorship: Sponsorship,
    filing_webhook_event: FilingWebhookEvent,
    page_count: int,
) -> None:
    """
    This method adds a new entry in the general ledger (transactions table)
    after a document has been successfully purchased.

    This method also creates a note for the new entry using data from the docket
    webhook event and the subscription record.

    Args:
        sponsorship (Sponsorship): The Sponsorship record used to complete the purchase.
        filing_webhook_event (FilingWebhookEvent): The docket webhook event related to the document.
        page_count (int): The number of pages in the PDF file.
    """

    note = f"Purchase {filing_webhook_event}"
    if filing_webhook_event.subscription:
        docket_number = filing_webhook_event.subscription.docket_number
        court_name = filing_webhook_event.subscription.court_name
        court_id = filing_webhook_event.subscription.pacer_court_id
        note += f"({docket_number}) in {court_name}({court_id})"

    Transaction.objects.create(
        user=sponsorship.user,
        sponsorship=sponsorship,
        type=Transaction.DOCUMENT_PURCHASE,
        amount=3.0 if page_count >= 30 else page_count * 0.10,
        note=note,
    )
