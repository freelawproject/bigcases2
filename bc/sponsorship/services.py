from decimal import Decimal

from django.conf import settings
from django.db.models import QuerySet
from django_rq.queues import get_queue
from rq import Retry

from bc.channel.models import Group
from bc.sponsorship.selectors import get_sponsorships_for_subscription
from bc.sponsorship.utils import (
    get_email_threshold_index,
    send_low_fund_email_to_curators,
)
from bc.subscription.types import Document

from .models import Transaction

queue = get_queue("default")


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
        document_cost = Decimal(
            document.get_price()
            * sponsorship.groups.count()
            / sponsored_groups.count()
        )

        threshold_idx = get_email_threshold_index(sponsorship.current_amount)
        threshold_value = (
            settings.LOW_FUNDING_EMAIL_THRESHOLDS[threshold_idx]
            if threshold_idx is not None
            else None
        )

        if (
            threshold_value
            and threshold_value > sponsorship.current_amount - document_cost
        ):
            # Purchase will cross low funding threshold. Send an email.
            group = sponsorship.groups.first()
            queue.enqueue(
                send_low_fund_email_to_curators,
                threshold_idx,
                group.pk,  # type: ignore
                sponsorship.pk,
                sponsorship.current_amount - Decimal(document_cost),
                retry=Retry(
                    max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                    interval=settings.RQ_RETRY_INTERVAL,
                ),
            )

        Transaction.objects.create(
            user=sponsorship.user,
            sponsorship=sponsorship,
            type=Transaction.DOCUMENT_PURCHASE,
            amount=document_cost,
            note=document.get_note(),
        )
