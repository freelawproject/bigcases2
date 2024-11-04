from django.db import models
from django.urls import reverse

from bc.core.models import AbstractDateTimeModel
from bc.core.utils.color import format_color_str
from bc.sponsorship.models import Sponsorship
from bc.users.models import User

from .utils.connectors.base import BaseAPIConnector
from .utils.connectors.bluesky import BlueskyConnector
from .utils.connectors.masto import MastodonConnector, get_handle_parts
from .utils.connectors.threads import ThreadsConnector
from .utils.connectors.twitter import TwitterConnector


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

    TWITTER = 1
    MASTODON = 2
    BLUESKY = 3
    THREADS = 4
    CHANNELS = (
        (TWITTER, "Twitter"),
        (MASTODON, "Mastodon"),
        (BLUESKY, "Bluesky"),
        (THREADS, "Threads"),
    )
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
            "Service's ID number, username, etc. for the account, "
            "if applicable"
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

    def get_api_wrapper(self) -> BaseAPIConnector:
        match self.service:
            case self.TWITTER:
                return TwitterConnector(
                    self.access_token, self.access_token_secret, self.account
                )
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
            case self.TWITTER:
                return f"https://twitter.com/{self.account}"
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
        help_text="The object's id returned by Twitter/Mastodon/etc's API",
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
            case Channel.TWITTER:
                return f"{self_url}/status/{self.object_id}"
            case Channel.BLUESKY:
                return f"{self_url}/post/{self.object_id}"
            case _:
                raise NotImplementedError(f"Unknown service: '{service}'.")
