from django.db import models
from django.db.models import Q


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


class BannerConfig(models.Model):

    is_active = models.BooleanField(
        default=False,
        help_text="If another config is currently active, enabling this one will deactivate the first one.",
    )
    banner_title = models.CharField(max_length=255)
    banner_text = models.TextField()
    banner_button_text = models.CharField(max_length=40)
    banner_button_link = models.URLField()

    class Meta:
        # This constraint ensures that only one BannerConfig
        # can have is_active = True at any given time.
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="only_one_active_banner",
            )
        ]

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"{self.pk}: {self.banner_title} ({status})"

    def save(self, *args, **kwargs):
        # If this banner is being activated, deactivate others.
        if self.is_active:
            # Deactivate all other active banners
            BannerConfig.objects.filter(is_active=True).exclude(
                pk=self.pk
            ).update(is_active=False)

        super().save(*args, **kwargs)
