from django.db import models

from bc.core.models import AbstractDateTimeModel
from bc.users.models import User

from .utils.masto import masto_regex


class Channel(AbstractDateTimeModel):
    """
    A "Channel" is a particular account on a service, which is used by
    BCB to broadcast or to issue commands to BCB.
    """

    service = models.CharField(
        help_text="Name of the service",
        max_length=100,
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
        help_text="Users that belong to the channel",
        related_name="channels",
    )
    enabled = models.BooleanField(
        help_text="Disabled by default; must enable manually", default=False
    )

    def self_url(self):
        if self.service == "twitter":
            return f"https://twitter.com/{self.account}"
        elif self.service == "mastodon":
            result = masto_regex.search(self.account)
            assert len(result.groups()) == 2
            account_part, instance_part = result.groups()
            return f"https://{instance_part}/@{account_part}"
        else:
            raise NotImplementedError(
                f"Channel.self_url() not yet implemented for service {self.service}"
            )
