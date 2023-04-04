from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Sponsorship, Transaction
from .utils import update_sponsorships_current_amount


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


@receiver(post_save, sender=Transaction)
def transaction_handler(sender, instance=None, created=False, **kwargs):
    if created and instance.type == Transaction.DOCUMENT_PURCHASE:
        """
        make sure We update the sponsorship's current_amount only if
        the django atomic transaction successfully commits.
        """
        transaction.on_commit(
            lambda: update_sponsorships_current_amount(instance)
        )
