from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from databyte.utils import compute_instance_storage, compute_child_storage, compute_external_storage, \
    compute_file_fields_storage, notify_parents_to_recompute


@receiver(post_save)
def update_storage_on_save(sender, instance: models.Model, **kwargs) -> None:
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
    if hasattr(
            instance, 'AutomatedStorageTrackingField'
    ) and instance.AutomatedStorageTrackingField.include_in_parents_count:
        notify_parents_to_recompute(instance)
