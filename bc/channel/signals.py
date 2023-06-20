from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django_rq.queues import get_queue
from rq import Retry

from bc.core.utils.cloudfront import create_cache_invalidation

from .models import Group

queue = get_queue("default")


@receiver(post_save, sender=Group)
def group_handler(sender, instance=None, created=False, **kwargs):
    # fires a job to create a new invalidation
    if settings.AWS_CLOUDFRONT_DISTRIBUTION_ID and not settings.DEVELOPMENT:
        queue.enqueue(
            create_cache_invalidation,
            reverse("little_cases"),
            retry=Retry(
                max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                interval=settings.RQ_RETRY_INTERVAL,
            ),
        )
