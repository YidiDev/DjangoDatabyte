from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from databyte.fields import AutomatedStorageTrackingField
from databyte.utils import (
    compute_instance_storage,
    compute_child_storage,
    compute_external_storage,
    compute_file_fields_storage,
    notify_parents_to_recompute
)


@receiver(pre_save)
def update_storage_on_pre_save(sender, instance: models.Model, raw=False, **kwargs) -> None:
    """
    Signal handler that updates an instance's AutomatedStorageTrackingField before the object is saved to the database.

    For instances with a field of type AutomatedStorageTrackingField, this function computes the total storage used by
    the instance.
    The calculation includes storage from:
    - The instance's own fields
    - Any related child objects
    - Any external storage
    - Any file fields on the instance

    The calculated storage value is set on the instance's AutomatedStorageTrackingField field before saving.
    This reduces the number of required database writes by performing the calculation and update as part of the save
    operation.

    If the AutomatedStorageTrackingField has the attribute `include_in_parents_count` set to True, the function also
    triggers a re-computation of storage for the instance's parent objects.

    Args:
        sender (Model): The class of the model sending the signal.
        instance (Model): The instance being saved.
        raw (bool): If True, the signal handler will be skipped (e.g., for raw database saves). Defaults to False.
        **kwargs: Additional keyword arguments.

    Notes:
        - This is a pre-save signal, designed to minimize the number of database writes.
        - The signal handler checks the `raw` parameter to determine whether to proceed with the storage computation.
    """

    if raw:
        return

    for field in instance._meta.fields:
        if isinstance(field, AutomatedStorageTrackingField):

            instance_storage: int = compute_instance_storage(instance)
            child_storage: int = compute_child_storage(instance)
            external_storage: int = compute_external_storage(instance)
            file_storage: int = compute_file_fields_storage(instance)

            storage_used_value: int = instance_storage + child_storage + external_storage + file_storage
            setattr(instance, field.name, storage_used_value)

            if field.include_in_parents_count:
                notify_parents_to_recompute(instance)


@receiver(post_delete)
def update_storage_on_delete(sender, instance: models.Model, **kwargs) -> None:
    """
    Signal handler that notifies parent instances to recompute their storage when an instance with
    a field of type AutomatedStorageTrackingField is deleted.

    If the instance's AutomatedStorageTrackingField field has the `include_in_parents_count` attribute set to True,
    this handler will notify the parent instances to recompute their storage to reflect the deletion.

    Args:
        sender (Model): The class of the model sending the signal.
        instance (Model): The instance being deleted.
        **kwargs: Additional keyword arguments.
    """

    for field in instance._meta.fields:
        if isinstance(field, AutomatedStorageTrackingField):
            if field.include_in_parents_count:
                notify_parents_to_recompute(instance)
                break
