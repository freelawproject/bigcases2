import logging
from datetime import timedelta

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django_rq.queues import get_queue
from rq import Retry

from bc.core.utils.cloudfront import create_cache_invalidation

from .models import Channel, Group
from .tasks import refresh_threads_access_token

queue = get_queue("default")

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Group)
def group_handler(sender, instance=None, created=False, **kwargs):
    # fires a job to create a new invalidation
    if settings.AWS_CLOUDFRONT_DISTRIBUTION_ID and not settings.DEVELOPMENT:
        if instance.is_big_cases:
            root_url = reverse("big_cases_about")
        else:
            root_url = f"{reverse('little_cases')}*"
        queue.enqueue(
            create_cache_invalidation,
            root_url,
            retry=Retry(
                max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                interval=settings.RQ_RETRY_INTERVAL,
            ),
        )


@receiver(post_save, sender=Channel)
def channel_handler(sender, instance=None, created=False, **kwargs):
    # create a new invalidation after changing data of a channel
    if not instance.group:
        return

    if settings.AWS_CLOUDFRONT_DISTRIBUTION_ID and not settings.DEVELOPMENT:
        if instance.group.is_big_cases:
            root_url = reverse("big_cases_about")
        else:
            root_url = f"{reverse('little_cases')}*"
        queue.enqueue(
            create_cache_invalidation,
            root_url,
            retry=Retry(
                max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                interval=settings.RQ_RETRY_INTERVAL,
            ),
        )

    # Schedule initial token refresh 2 days after creation
    if created and instance.service == Channel.THREADS:
        queue.enqueue_in(
            timedelta(days=2),
            refresh_threads_access_token,
            channel_pk=instance.pk,
            retry=Retry(
                max=settings.RQ_MAX_NUMBER_OF_RETRIES,
                interval=settings.RQ_RETRY_INTERVAL,
            ),
        )
        logger.info(
            f"Scheduled new refresh token for newly created channel {instance} in 2 days"
        )
