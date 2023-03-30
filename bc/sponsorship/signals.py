from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Sponsorship, Transaction


@receiver(post_save, sender=Sponsorship)
def sponsorship_handler(sender, instance=None, created=False, **kwargs):
    if created:
        instance.current_amount = instance.original_amount
        instance.save()

        Transaction.objects.create(
            user=instance.user,
            sponsorship=instance,
            amount=instance.original_amount,
        )
