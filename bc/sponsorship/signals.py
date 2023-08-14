from django.conf import settings
from django.db import transaction as db_transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django_rq.queues import get_queue
from rq import Retry

from bc.core.utils.cloudfront import create_cache_invalidation

from .models import Sponsorship, Transaction
from .utils import update_sponsorships_current_amount

queue = get_queue("default")


@receiver(post_save, sender=Sponsorship)
def sponsorship_handler(sender, instance=None, created=False, **kwargs):
    if created:
        instance.current_amount = instance.original_amount
        instance.save()

        Transaction.objects.create(
            user=instance.user,
            sponsorship=instance,
            amount=instance.original_amount,
        )

        # fires a job to create a new invalidation
        if (
            settings.AWS_CLOUDFRONT_DISTRIBUTION_ID
            and not settings.DEVELOPMENT
        ):
            queue.enqueue(
                create_cache_invalidation,
                reverse("big_cases_sponsors"),
                retry=Retry(
                    max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                    interval=settings.RQ_RETRY_INTERVAL,
                ),
            )


@receiver(post_save, sender=Transaction)
def transaction_handler(sender, instance=None, created=False, **kwargs):
    if created and instance.type == Transaction.DOCUMENT_PURCHASE:
        """
        make sure We update the sponsorship's current_amount only if
        the django atomic transaction successfully commits.
        """
        db_transaction.on_commit(
            lambda: update_sponsorships_current_amount(instance)
        )
