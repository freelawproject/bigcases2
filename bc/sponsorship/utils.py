from decimal import Decimal

from .models import Sponsorship, Transaction


def update_sponsorships_current_amount(ledger_entry: Transaction) -> None:
    if not ledger_entry.sponsorship_id:
        return None
    sponsorship = Sponsorship.objects.get(pk=ledger_entry.sponsorship_id)
    sponsorship.current_amount -= Decimal(ledger_entry.amount)
    sponsorship.save()
