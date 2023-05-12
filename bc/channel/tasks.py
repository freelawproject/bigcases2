from django.conf import settings
from django_rq.queues import get_queue
from rq import Retry

from .models import Channel, Group

queue = get_queue("default")


def enqueue_text_status_for_channel(channel: Channel, text: str) -> None:
    """
    Enqueue a job to create a new status with only text in the given
    channel.

    Args:
        channel (Channel): The channel object.
        text (str): Message for the new status.
    """
    api = channel.get_api_wrapper()
    queue.enqueue(
        api.add_status,
        text,
        retry=Retry(
            max=settings.RQ_MAX_NUMBER_OF_RETRIES,
            interval=settings.RQ_RETRY_INTERVAL,
        ),
    )


def enqueue_text_status_for_group(group: Group, text: str) -> None:
    """
    Enqueue a job to create a new status in each channel linked to the
    given group.

    Args:
        group (Group): The given group.
        text (str): Message for the post.
    """
    for channel in group.channels.all():
        enqueue_text_status_for_channel(channel, text)
