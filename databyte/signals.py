from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save)
def update_storage(sender, instance, **kwargs):
    # Check if the instance has an AutomatedStorageTrackingField
    if hasattr(instance, 'AutomatedStorageTrackingField'):
        # Compute the storage here and update the instance's value
        # (Consider recursively checking children records as described)

        # Update parent records if include_in_parents_count is True
        if instance.AutomatedStorageTrackingField.include_in_parents_count:
            # Find parent records and force them to update their count
            pass
