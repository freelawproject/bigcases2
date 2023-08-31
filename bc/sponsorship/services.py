from django.db.models import QuerySet

from bc.channel.models import Group
from bc.sponsorship.selectors import get_sponsorships_for_subscription
from bc.subscription.types import Document

from .models import Transaction


def log_purchase(
    sponsored_groups: QuerySet[Group], subscription_pk: int, document: Document
) -> None:
    """
    This method adds a new entry in the general ledger (transactions table) for
    each active sponsorship that's related to docked linked to the webhook event
    after a document has been successfully purchased.

    This method also creates a note for the new entry using data from the docket
    webhook event and the subscription record.

    Args:
        sponsored_groups (Sponsorship): Set of sponsored channels groups following the case.
        subscription_pk (int): PK of the subscription record related to the document.
        document (Document): Document instance that stores data of the file that was bought.
    """
    # Gets the ids of the active sponsorships from each sponsor group.
    sponsorship_ids: list[int] = [
        group.sponsorships.first().pk for group in sponsored_groups if group.sponsorships.count()  # type: ignore
    ]
    sponsorships = get_sponsorships_for_subscription(
        sponsorship_ids, subscription_pk
    )

    for sponsorship in sponsorships:
        Transaction.objects.create(
            user=sponsorship.user,
            sponsorship=sponsorship,
            type=Transaction.DOCUMENT_PURCHASE,
            amount=document.get_price()
            * sponsorship.groups.count()
            / sponsored_groups.count(),
            note=document.get_note(),
        )
