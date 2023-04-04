from decimal import Decimal

from django.db.models import F

from .models import Transaction


def update_sponsorships_current_amount(ledger_entry: Transaction) -> None:
    """
    This method updates the current_amount field of the sponsorship record
    related to the given ledger entry after a document has been purchased.

    Args:
        ledger_entry (Transaction): The transaction object related to the purchase.
    """
    if not ledger_entry.sponsorship:
        return None
    sponsorship = ledger_entry.sponsorship
    sponsorship.current_amount = F("current_amount") - Decimal(
        ledger_entry.amount
    )
    sponsorship.save()
