from django.db import models

from bc.core.models import AbstractDateTimeModel
from bc.sponsorship.models import Sponsorship
from bc.users.models import User

from .utils.connectors.base import BaseAPIConnector
from .utils.connectors.masto import MastodonConnector, get_server_url
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

    def __str__(self) -> str:
        return f"{self.pk}: {self.name}"


class Channel(AbstractDateTimeModel):
    """
    A "Channel" is a particular account on a service, which is used by
    BCB to broadcast or to issue commands to BCB.
    """

    TWITTER = 1
    MASTODON = 2
    CHANNELS = (
        (TWITTER, "Twitter"),
        (MASTODON, "Mastodon"),
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
                    self.access_token, self.access_token_secret
                )
            case self.MASTODON:
                return MastodonConnector(
                    self.access_token, get_server_url(self.account)
                )
            case _:
                raise NotImplementedError(
                    f"No wrapper implemented for service: '{self.service}'."
                )

    def self_url(self):
        if self.service == self.TWITTER:
            return f"https://twitter.com/{self.account}"
        elif self.service == self.MASTODON:
            result = masto_regex.search(self.account)
            assert len(result.groups()) == 2
            account_part, instance_part = result.groups()
            return f"https://{instance_part}/@{account_part}"
        else:
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
    object_id = models.PositiveBigIntegerField(
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
        match service:
            case Channel.MASTODON:
                return f"https://law.builders/@bigcases/{ self.object_id }"
            case Channel.TWITTER:
                return (
                    f"https://twitter.com/big_cases/status/{ self.object_id }"
                )
            case _:
                raise NotImplementedError(f"Unknown service: '{ service }'.")
