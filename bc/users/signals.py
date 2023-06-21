from datetime import timedelta

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now


@receiver(
    post_save,
    sender=settings.AUTH_USER_MODEL,
    dispatch_uid="create_superuser_object",
)
def superuser_creation(sender, instance, created, **kwargs):
    """
    Populates fields related to authentication in the user model for
    records created using the createsuperuser command.

    We need to do this to allow superuser accounts to login using the
    custom form that implements the ConfirmedEmailAuthenticationForm class.
    """
    if created and instance.is_superuser:
        instance.email_confirmed = True

        instance.save(update_fields=["email_confirmed"])
