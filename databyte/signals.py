from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from databyte.utils import (
    compute_instance_storage,
    compute_child_storage,
    compute_external_storage,
    compute_file_fields_storage,
    notify_parents_to_recompute
)


@receiver(post_save)
def update_storage_on_save(sender, instance: models.Model, **kwargs) -> None:
    """
    Signal handler that updates the AutomatedStorageTrackingField of an instance upon saving.

    If the instance has an AutomatedStorageTrackingField attribute, this handler will compute
    the total storage consumed by the instance by aggregating storage from various sources
    (instance's fields, child objects, external storage, and file fields). The calculated
    value will then be saved to the instance's AutomatedStorageTrackingField.

    If the field's `include_in_parents_count` attribute is set to True, this handler will
    also notify the instance's parents to recompute their storage.

    Args:
        sender (Model): The model class.
        instance (Model): The actual instance being saved.
        **kwargs: Additional keyword arguments.
    """
    if hasattr(instance, 'AutomatedStorageTrackingField'):
        instance_storage: int = compute_instance_storage(instance)
        child_storage: int = compute_child_storage(instance)
        external_storage: int = compute_external_storage(instance)
        file_storage: int = compute_file_fields_storage(instance)

        instance.AutomatedStorageTrackingField = instance_storage + child_storage + external_storage + file_storage
        instance.save(update_fields=['AutomatedStorageTrackingField'])

        if instance.AutomatedStorageTrackingField.include_in_parents_count:
            notify_parents_to_recompute(instance)


@receiver(post_delete)
def update_storage_on_delete(sender, instance: models.Model, **kwargs) -> None:
    """
    Signal handler that notifies parent instances to recompute their storage when an instance with
    AutomatedStorageTrackingField is deleted.

    If the instance's AutomatedStorageTrackingField has its `include_in_parents_count` attribute set to True,
    the parents of this instance will be notified to recompute their storage to reflect the deletion.

    Args:
        sender (Model): The model class.
        instance (Model): The actual instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    if hasattr(
            instance, 'AutomatedStorageTrackingField'
    ) and instance.AutomatedStorageTrackingField.include_in_parents_count:
        notify_parents_to_recompute(instance)
