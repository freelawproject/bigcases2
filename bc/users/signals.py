from datetime import timedelta

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from bc.core.utils.crypto import sha1_activation_key


@receiver(
    post_save,
    sender=settings.AUTH_USER_MODEL,
    dispatch_uid="create_superuser_object",
)
def superuser_creation(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        instance.activation_key = sha1_activation_key(instance.username)
        instance.key_expires = now() + timedelta(days=5)
        instance.email_confirmed = True

        instance.save(
            update_fields=["activation_key", "key_expires", "email_confirmed"]
        )
