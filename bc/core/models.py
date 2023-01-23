from django.db import models


class AbstractDateTimeModel(models.Model):
    """An abstract base class for most models"""

    date_created = models.DateTimeField(
        help_text="The moment when the item was created.",
        auto_now_add=True,
        db_index=True,
    )
    date_modified = models.DateTimeField(
        help_text="The last moment when the item was modified. A value in year"
                  " 1750 indicates the value is unknown",
        auto_now=True,
        db_index=True,
    )

    class Meta:
        abstract = True
