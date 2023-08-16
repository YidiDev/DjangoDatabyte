from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from databyte.utils import compute_instance_storage, compute_child_storage, compute_external_storage, \
    compute_file_fields_storage


# noinspection PyProtectedMember
@receiver([post_save, post_delete])
def update_storage(sender, instance, **kwargs):
    # Check if the instance has an AutomatedStorageTrackingField
    if hasattr(instance, 'AutomatedStorageTrackingField'):
        # Compute the instance's storage, child storage, and external storage
        instance_storage = compute_instance_storage(instance)
        child_storage = compute_child_storage(instance)
        external_storage = compute_external_storage(instance)
        file_storage = compute_file_fields_storage(instance)

        # Update the instance's AutomatedStorageTrackingField value
        instance.AutomatedStorageTrackingField = instance_storage + child_storage + external_storage + file_storage
        instance.save(update_fields=['AutomatedStorageTrackingField'])

        # Signal parent records to update if required
        if instance.AutomatedStorageTrackingField.include_in_parents_count:
            for field in instance._meta.fields:
                if isinstance(
                        field, models.ForeignKey
                ) and hasattr(field.related_model, 'AutomatedStorageTrackingField'):
                    parent = getattr(instance, field.name)
                    parent.save()
