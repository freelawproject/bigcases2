from django.db import models

from bc.core.models import AbstractDateTimeModel
from bc.users.models import User


class Sponsorship(AbstractDateTimeModel):
    user = models.ForeignKey(
        User,
        help_text="The user sponsoring the Bot",
        related_name="sponsorships",
        on_delete=models.PROTECT,
    )
    original_amount = models.DecimalField(
        help_text="Initial amount of money given by the sponsor",
        max_digits=10,
        decimal_places=2,
    )
    current_amount = models.DecimalField(
        help_text="Amount of money that's left to buy documents",
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    watermark_message = models.CharField(
        help_text="Short message to include in document's thumbnails",
        max_length=100,
        default="",
    )

    def __str__(self) -> str:
        return f"{self.pk}: {self.user.username} - {self.original_amount}"


class Transaction(AbstractDateTimeModel):
    SPONSORSHIP = 1
    DOCUMENT_PURCHASE = 2
    ADJUSTMENT = 3
    TYPES = (
        (SPONSORSHIP, "Sponsorship"),
        (DOCUMENT_PURCHASE, "Document Purchase"),
        (ADJUSTMENT, "Adjustment"),
    )

    user = models.ForeignKey(
        User,
        help_text="User associated with the transaction",
        related_name="transactions",
        on_delete=models.PROTECT,
    )
    sponsorship = models.ForeignKey(
        Sponsorship,
        help_text="Sponsorship record related to the transaction",
        related_name="transactions",
        null=True,
        on_delete=models.PROTECT,
    )
    type = models.SmallIntegerField(
        help_text=f"The type of the transaction. Possible values are: {', '.join([f'({t[0]}): {t[1]}' for t in TYPES])}",
        default=SPONSORSHIP,
        choices=TYPES,
    )
    amount = models.DecimalField(
        help_text="Amount of money spent/received in the transaction",
        max_digits=10,
        decimal_places=2,
    )
    note = models.TextField(
        help_text="More information about the transaction",
    )

    def __str__(self) -> str:
        return f"{self.pk}: {self.get_type_display()}"
