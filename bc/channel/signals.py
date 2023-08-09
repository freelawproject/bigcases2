from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django_rq.queues import get_queue
from rq import Retry

from bc.core.utils.cloudfront import create_cache_invalidation

from .models import Channel, Group

queue = get_queue("default")


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
def group_handler(sender, instance=None, created=False, **kwargs):
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
