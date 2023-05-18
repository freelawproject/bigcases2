from django.db.models import QuerySet

from bc.channel.models import Group
from bc.sponsorship.selectors import get_sponsorships_for_subscription
from bc.subscription.models import FilingWebhookEvent

from .models import Transaction


def log_purchase(
    sponsored_groups: QuerySet[Group],
    filing_webhook_event: FilingWebhookEvent,
    page_count: int,
) -> None:
    """
    This method adds a new entry in the general ledger (transactions table) for
    each active sponsorship that's related to docked linked to the webhook event
    after a document has been successfully purchased.

    This method also creates a note for the new entry using data from the docket
    webhook event and the subscription record.

    Args:
        sponsored_groups (Sponsorship): Set of channels groups with available sponsorships.
        filing_webhook_event (FilingWebhookEvent): The docket webhook event related to the document.
        page_count (int): The number of pages in the PDF file.
    """
    document_price = 3.0 if page_count >= 30 else page_count * 0.10
    note = f"Purchase {filing_webhook_event}"
    if filing_webhook_event.subscription:
        docket_number = filing_webhook_event.subscription.docket_number
        court_name = filing_webhook_event.subscription.court_name
        court_id = filing_webhook_event.subscription.pacer_court_id
        note += f"({docket_number}) in {court_name}({court_id})"

    sponsorship_ids = [
        group.sponsorships.first().pk for group in sponsored_groups
    ]
    sponsorships = get_sponsorships_for_subscription(
        sponsorship_ids, filing_webhook_event.subscription.pk
    )

    for sponsorship in sponsorships:
        Transaction.objects.create(
            user=sponsorship.user,
            sponsorship=sponsorship,
            type=Transaction.DOCUMENT_PURCHASE,
            amount=document_price
            * sponsorship.groups.count()
            / sponsored_groups.count(),
            note=note,
        )
