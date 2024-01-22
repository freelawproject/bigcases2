from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django_rq.queues import get_queue
from rq import Retry

from bc.channel.models import Group
from bc.channel.selectors import get_groups_with_low_funding
from bc.sponsorship.emails import emails
from bc.sponsorship.models import Sponsorship
from bc.sponsorship.selectors import get_total_documents_purchased_by_group_id
from bc.users.selectors import get_curators_by_channel_group_id
from bc.users.utils.email import EmailType

from .models import Transaction

queue = get_queue("default")


def send_low_fund_email_to_curators(group_id: int) -> None:
    """Sends emails to curator users of the given group.

    Args:
        group_id (int): The ID of the channel group to send emails to.
    """
    group = Group.objects.get(pk=group_id)
    curators = get_curators_by_channel_group_id(group_id)
    total_purchases = get_total_documents_purchased_by_group_id(group_id)
    curators_emails = list(curators.values_list("email", flat=True))

    email: EmailType = emails["low_funds_alert"]
    body = email["body"] % (group.name, total_purchases)
    send_mail(
        email["subject"],
        body,
        email["from_email"],
        curators_emails,
    )
    cache_key = f"low-funding:{group_id}"
    # Save the idempotency key for 7 days
    cache.set(cache_key, True, 60 * 60 * 24 * 7)


def update_sponsorships_current_amount(ledger_entry: Transaction) -> None:
    """
    This method updates the current_amount field of the sponsorship record
    related to the given ledger entry after a document has been purchased.

    It also schedules a task to send an alert when the funds of a group are
    running low.

    Args:
        ledger_entry (Transaction): The transaction object related to the purchase.
    """
    if not ledger_entry.sponsorship:
        return None

    # lock sponsorship record while updating the current_value and
    # checking whether we should send a low fund email
    with transaction.atomic():
        sponsorship = Sponsorship.objects.select_for_update().get(
            pk=ledger_entry.sponsorship_id
        )
        sponsorship.current_amount = F("current_amount") - Decimal(
            ledger_entry.amount
        )
        sponsorship.save()

        channel_group_ids = list(
            sponsorship.groups.all().values_list("id", flat=True)
        )
        low_funding_query = get_groups_with_low_funding()
        low_funding_groups = low_funding_query.filter(pk__in=channel_group_ids)

        if not low_funding_groups.exists():
            return None

        for group in low_funding_groups:
            # try to get cache key for the group
            cache_key = f"low-funding:{group.pk}"
            already_notified_group = cache.get(cache_key)

            # skip the group if the key is still in cache
            if already_notified_group:
                continue

            queue.enqueue(
                send_low_fund_email_to_curators,
                group.pk,
                retry=Retry(
                    max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                    interval=settings.RQ_RETRY_INTERVAL,
                ),
            )
