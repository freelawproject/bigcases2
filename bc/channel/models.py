import logging

from django.db import models
from django.urls import reverse
from redis.exceptions import LockError

from bc.core.models import AbstractDateTimeModel
from bc.core.utils.color import format_color_str
from bc.core.utils.redis import make_redis_interface
from bc.sponsorship.models import Sponsorship
from bc.users.models import User

from .utils.connectors.base import (
    BaseAPIConnector,
    RefreshableBaseAPIConnector,
)
from .utils.connectors.bluesky import BlueskyConnector
from .utils.connectors.masto import MastodonConnector, get_handle_parts
from .utils.connectors.threads import ThreadsConnector

logger = logging.getLogger(__name__)

r = make_redis_interface("CACHE")


class Group(AbstractDateTimeModel):
    name = models.CharField(
        help_text="Name for a set of channels",
        max_length=100,
    )
    is_big_cases = models.BooleanField(
        help_text="Designates whether this group should be treated as the set of big cases channels",
        default=False,
    )
    sponsorships = models.ManyToManyField(
        Sponsorship,
        related_name="groups",
        blank=True,
    )
    slug = models.SlugField(
        help_text="A generated path for this item", default=""
    )
    overview = models.TextField(
        help_text="Short description of the purpose of this group", default=""
    )
    border_color = models.CharField(
        help_text="Color used in the images' borders of this group",
        max_length=7,
        default="#F3C33E",
    )

    def __str__(self) -> str:
        return f"{self.pk}: {self.name}"

    def get_absolute_url(self):
        return reverse("little_cases_detail", args=[self.slug])

    @property
    def border_color_rgb(self) -> tuple[int, ...]:
        rgb = format_color_str(self.border_color)
        if not rgb:
            # we return the default yellow border if we fail to parse the hex str
            return (243, 195, 62)
        return rgb


class Channel(AbstractDateTimeModel):
    """
    A "Channel" is a particular account on a service, which is used by
    BCB to broadcast or to issue commands to BCB.
    """

    # TWITTER = 1 Twitter is deprecated, leaving this for documentation.
    MASTODON = 2
    BLUESKY = 3
    THREADS = 4
    CHANNELS = (
        (MASTODON, "Mastodon"),
        (BLUESKY, "Bluesky"),
        (THREADS, "Threads"),
    )
    CHANNELS_TO_REFRESH = [THREADS]
    service = models.PositiveSmallIntegerField(
        help_text="Type of the service",
        choices=CHANNELS,
    )
    account = models.CharField(
        help_text="Name of the account",
        max_length=100,
    )
    account_id = models.CharField(
        help_text=(
            "Service's ID number, username, etc. for the account, if applicable"
        ),
        max_length=100,
    )
    user = models.ManyToManyField(
        User,
        help_text="Users that can send commands to the bot through the channel",
        related_name="channels",
        blank=True,
    )
    enabled = models.BooleanField(
        help_text="Disabled by default; must enable manually", default=False
    )
    group = models.ForeignKey(
        "Group", related_name="channels", null=True, on_delete=models.SET_NULL
    )
    access_token = models.TextField(
        help_text="Access Tokens of the account that the bot is making the request on behalf of",
        default="",
    )
    access_token_secret = models.TextField(
        help_text="Access Tokens Secret of the account that the bot is making the request on behalf of",
        default="",
        blank=True,
    )

    def get_api_wrapper(
        self,
    ) -> BaseAPIConnector | RefreshableBaseAPIConnector:
        match self.service:
            case self.MASTODON:
                account_part, instance_part = get_handle_parts(self.account)
                return MastodonConnector(
                    self.access_token, instance_part, account_part
                )
            case self.BLUESKY:
                return BlueskyConnector(self.account_id, self.access_token)
            case self.THREADS:
                return ThreadsConnector(
                    self.account, self.account_id, self.access_token
                )
            case _:
                raise NotImplementedError(
                    f"No wrapper implemented for service: '{self.service}'."
                )

    def self_url(self):
        match self.service:
            case self.MASTODON:
                account_part, instance_part = get_handle_parts(self.account)
                return f"{instance_part}@{account_part}"
            case self.BLUESKY:
                return f"https://bsky.app/profile/{self.account_id}"
            case self.THREADS:
                return f"https://www.threads.net/@{self.account}"
            case _:
                raise NotImplementedError(
                    f"Channel.self_url() not yet implemented for service {self.service}"
                )

    def validate_access_token(self):
        """
        Validates and refreshes the access token for the channel if necessary.

        This method implements a locking mechanism to avoid multiple tasks
        from concurrently trying to validate the same token.
        """
        if self.service not in self.CHANNELS_TO_REFRESH:
            return
        lock_key = self._get_refresh_lock_key()
        lock = r.lock(lock_key, sleep=1, timeout=60)
        blocking_timeout = 60
        try:
            # Use a blocking lock to wait until locking task is finished
            lock.acquire(blocking=True, blocking_timeout=blocking_timeout)
            # Then perform action to validate
            self._refresh_access_token()
        except LockError as e:
            logger.error(
                f"LockError while acquiring lock for channel {self}: {e}"
            )
            raise e
        finally:
            if lock.owned():
                try:
                    lock.release()
                except Exception as e:
                    logger.error(
                        f"Error releasing lock for channel {self}:\n{e}"
                    )

    def _refresh_access_token(self):
        api = self.get_api_wrapper()
        try:
            refreshed, access_token = api.validate_access_token()
            if refreshed:
                self.access_token = access_token
                self.save()
        except Exception as e:
            logger.error(
                f"Error when trying to refresh token for channel {self.pk}:\n{e}"
            )

    def _get_refresh_lock_key(self):
        """
        Constructs the Redis key used for locking during access token refresh.
        """
        return f"token_refresh_lock_{self.account_id}@{self.get_service_display()}"

    def __str__(self) -> str:
        if self.account:
            return f"{self.pk}: {self.account}"
        return f"{self.pk}"


class Post(AbstractDateTimeModel):
    filing_webhook_event = models.ForeignKey(
        "subscription.FilingWebhookEvent",
        related_name="posts",
        on_delete=models.CASCADE,
    )
    channel = models.ForeignKey(
        "Channel", related_name="posts", on_delete=models.CASCADE
    )
    object_id = models.CharField(
        help_text="The object's id returned by Bluesky/Mastodon/etc's API",
    )
    text = models.TextField(
        help_text="The post content",
        blank=True,
    )

    def __str__(self) -> str:
        return (
            f"{self.filing_webhook_event.__str__()} on {self.channel.service}"
        )

    @property
    def post_url(self) -> str:
        service = self.channel.service
        self_url = self.channel.self_url()

        match service:
            case Channel.MASTODON:
                return f"{self_url}/{self.object_id}"
            case Channel.BLUESKY:
                return f"{self_url}/post/{self.object_id}"
            case _:
                raise NotImplementedError(f"Unknown service: '{service}'.")
