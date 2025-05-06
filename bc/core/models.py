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


class BannerConfig(models.Model):
    is_active = models.BooleanField(
        default=False,
        help_text="If another config is currently active, enabling this one will deactivate the first one.",
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    button_text = models.CharField(max_length=40, null=True, blank=True)
    button_link = models.URLField(null=True, blank=True)

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        title = self.title or "Banner"
        return f"{self.pk}: {title} ({status})"

    def save(self, *args, **kwargs):
        # If this banner is being activated, deactivate others.
        if self.is_active:
            # Deactivate all other active banners
            BannerConfig.objects.filter(is_active=True).exclude(
                pk=self.pk
            ).update(is_active=False)

        super().save(*args, **kwargs)
