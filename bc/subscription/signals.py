from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq.queues import get_queue
from rq import Retry

from bc.core.utils.cloudfront import create_cache_invalidation

from .models import Subscription

queue = get_queue("default")


@receiver(post_save, sender=Subscription)
def subscription_handler(sender, instance=None, created=False, **kwargs):
    if (
        created
        and settings.AWS_CLOUDFRONT_DISTRIBUTION_ID
        and not settings.DEVELOPMENT
    ):
        # fires a job to create a new invalidation
        queue.enqueue(
            create_cache_invalidation,
            "/*",
            retry=Retry(
                max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                interval=settings.RQ_RETRY_INTERVAL,
            ),
        )
