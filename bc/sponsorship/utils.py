from decimal import Decimal

from django.core.mail import send_mail
from django.db.models import F

from bc.channel.models import Group
from bc.sponsorship.selectors import get_total_documents_purchased_by_group_id
from bc.users.selectors import get_curators_by_channel_group_id
from bc.users.utils.email import EmailType, emails

from .models import Transaction


def send_low_fund_email_to_curators(group_id: int) -> None:
    """Sends emails to curator users of the given group.

    Args:
        group_id (int): The ID of the channel group to send emails to.
    """
    group = Group.objects.get(pk=group_id)
    curators = get_curators_by_channel_group_id(group_id)
    total_purchases = get_total_documents_purchased_by_group_id(group_id)
    curators_emails = list(curators.values_list("email", flat=True))

    email: EmailType = emails["confirm_your_new_account"]
    body = email["body"] % (group.name, total_purchases)
    send_mail(
        email["subject"],
        body,
        email["from_email"],
        curators_emails,
    )


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
