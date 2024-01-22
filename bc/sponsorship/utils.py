from decimal import Decimal

from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import F

from bc.channel.models import Group
from bc.sponsorship.emails import emails
from bc.sponsorship.models import Sponsorship
from bc.users.selectors import get_curators_by_channel_group_id
from bc.users.utils.email import EmailType

from .models import Transaction


def get_email_threshold_index(current_amount: Decimal) -> int | None:
    """
    Retrieves the index of the first email threshold that is equal or lower
    than the current sponsorship amount.

    Args:
        current_amount (Decimal): Updated amount of the sponsorship

    Returns:
        int: index of the first threshold in the list that is lower than the
        current sponsorship amount, or None if all thresholds are higher than
        the current amount.

    Examples:
        thresholds = [1500, 1000, 500, 200, 100]
        current_amount = 800
        index = get_email_threshold_index(thresholds, current_amount)
        print(index)  # Output: 2 (500 is the first threshold lower than 800)


        thresholds = [1500, 1000, 500, 200, 100]
        current_amount = 10
        index = get_email_threshold_index(thresholds, current_amount)
        print(index)  # Output: None (all thresholds are higher than 10)
    """
    return next(
        (
            i
            for i, v in enumerate(settings.LOW_FUNDING_EMAIL_THRESHOLDS)
            if current_amount >= Decimal(v)
        ),
        None,
    )


def get_ordinal(n: int) -> str:
    """Converts a non-negative integer to its ordinal representation.

    Args:
        n (int): A non-negative integer.

    Returns:
        str: A string representing the ordinal form of the number.
    """
    # Handle cases for 11, 12, 13
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def send_low_fund_email_to_curators(
    threshold_idx: int,
    group_id: int,
    sponsorship_id: int,
    amount_remaining: float,
) -> None:
    """Sends emails to curator users of the given group.

    This method uses the threshold index to compute the subject of the email.

    Args:
        threshold_idx (int): Index of the email threshold.
        group_id (int): The ID of the channel group to send emails to.
        sponsorship_id (int): The ID of active sponsorship
        amount_remaining (float): The remaining amount of the sponsorship after
        buying the document.
    """
    group = Group.objects.get(pk=group_id)
    curators = get_curators_by_channel_group_id(group_id)
    sponsorship = Sponsorship.objects.select_related("user").get(
        pk=sponsorship_id
    )
    curators_emails = list(curators.values_list("email", flat=True))

    email_template: EmailType = emails["low_funds_alert"]
    core_subject = email_template["subject"].format(bot_name=group.name)
    if not threshold_idx:
        prefix_subject = "[Action Needed]"
    elif threshold_idx == len(settings.LOW_FUNDING_EMAIL_THRESHOLDS) - 1:
        prefix_subject = "[Action Needed, Final Notice]"
        curators_emails.append("info@free.law")
    else:
        ordinal = get_ordinal(threshold_idx + 1)
        prefix_subject = f"[Action Needed, {ordinal} Notice]"
    subject = f"{prefix_subject}: {core_subject}"

    body = email_template["body"].format(
        bot_name=group.name,
        original_amount=sponsorship.original_amount,
        amount_remaining=round(amount_remaining, 2),
    )
    # Send the alert to all the curators and the user associated to the
    # sponsorships. We add info@free.law to the list of emails for the
    # Final Notice alert.
    email = EmailMessage(
        subject,
        body,
        email_template["from_email"],
        to=[sponsorship.user.email],
        bcc=curators_emails,
    )
    email.send()


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
