import logging
from datetime import timedelta

import requests
from django.conf import settings
from django_rq.queues import get_queue
from rq import Retry

from .models import Channel, Group

queue = get_queue("default")

logger = logging.getLogger(__name__)


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
            interval=settings.RQ_POST_RETRY_INTERVALS,
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


def refresh_threads_access_token(channel_pk):
    """
    Task to refresh the access token for a Threads channel.
    """
    try:
        channel = Channel.objects.get(pk=channel_pk)
    except Channel.DoesNotExist:
        logger.warning(
            f"Trying to refresh Threads access token for channel {channel_pk} but it no longer exists."
        )
        return

    if channel.service != Channel.THREADS:
        logger.warning(
            f"Trying to refresh Threads access token for a {channel.get_service_display()} channel. Aborting."
        )
        return

    refresh_access_token_url = "https://graph.threads.net/refresh_access_token"
    params = {
        "grant_type": "th_refresh_token",
        "access_token": channel.access_token,
    }
    response = requests.get(refresh_access_token_url, params=params)

    if response.status_code != 200:
        logger.error(
            f"Failed to refresh access token for Threads channel {channel}:"
            f" {response.status_code} {response.text}"
        )
        return

    data = response.json()
    new_access_token = data.get("access_token")
    expires_in = data.get("expires_in")  # In seconds

    if new_access_token is None or expires_in is None:
        logger.error(
            f"Missing 'access_token' or 'expires_in' in refresh access token response for Threads channel {channel}: {data}\n"
            f"If the issue persists, a new access token can be retrieved manually with the script again."
        )
        return

    channel.access_token = new_access_token
    channel.save()

    # Schedule the next token refresh
    delay_seconds = (
        expires_in - 86400
    )  # Subtract one day to avoid expiration before the task runs
    queue.enqueue_in(
        timedelta(seconds=delay_seconds if delay_seconds > 0 else expires_in),
        refresh_threads_access_token,
        channel_pk=channel.pk,
        retry=Retry(
            max=settings.RQ_MAX_NUMBER_OF_RETRIES,
            interval=settings.RQ_RETRY_INTERVAL,
        ),
    )
    logger.info(
        f"Scheduled new refresh token for Threads channel {channel}"
        f" in {delay_seconds} seconds ({expires_in / 86400:.1f} days)"
    )
