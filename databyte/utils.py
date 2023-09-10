from django.core.exceptions import FieldDoesNotExist
from django.db import models
from databyte.fields import ExternalStorageTrackingField, StorageAwareForeignKey, AutomatedStorageTrackingField


def compute_instance_storage(instance: models.Model) -> int:
    total_storage: int = 0
    total_storage += compute_instance_fields_storage(instance)
    total_storage += compute_external_storage(instance)
    total_storage += compute_child_storage(instance)
    total_storage += compute_file_fields_storage(instance)
    return total_storage


# noinspection PyProtectedMember,PyTypeChecker
def compute_instance_fields_storage(instance: models.Model) -> int:
    """
    Compute the storage consumed by the fields of a given instance.

    Args:
        instance (Model): The instance for which storage is to be computed.

    Returns:
        int: Total storage (in bytes) consumed by the instance.
    """
    total_storage: int = 0
    for field in instance._meta.fields:
        value: models.Field | None = getattr(instance, field.name, None)
        if value is None:
            total_storage += 1
            continue
        if isinstance(
                field,
                (
                        models.CharField,
                        models.TextField,
                        models.EmailField,
                        models.URLField,
                        models.SlugField,
                        models.FileField,
                        models.ImageField
                )
        ):
            total_storage += len(value.encode('utf-8'))
        elif isinstance(
                field,
                (
                        ExternalStorageTrackingField,
                        AutomatedStorageTrackingField,
                        models.PositiveIntegerField,
                        models.BigIntegerField,
                        models.IntegerField,
                        models.AutoField,
                        models.PositiveSmallIntegerField,
                        models.SmallIntegerField
                )
        ):
            total_storage += 8
        elif isinstance(field, models.BooleanField):
            total_storage += 1
        elif isinstance(field, (models.DateField, models.TimeField, models.DateTimeField, models.DurationField)):
            total_storage += len(str(value).encode('utf-8'))
        elif isinstance(field, (models.FloatField, models.DecimalField)):
            total_storage += 8
        elif isinstance(field, models.BinaryField):
            total_storage += len(value)
        elif isinstance(field, models.UUIDField):
            total_storage += len(value.hex)
        elif isinstance(field, (StorageAwareForeignKey, models.ForeignKey)):
            total_storage += len(str(value.pk))
        else:
            total_storage += len(str(value).encode('utf-8'))
    return total_storage


# noinspection PyProtectedMember
def compute_child_storage(instance: models.Model) -> int:
    """
    Compute the storage consumed by the child records related to a given instance.

    This function iterates through the related objects of the instance, specifically looking for related models
    connected through fields of type StorageAwareForeignKey with the attribute `count_as_storage_parent` set to True.
    In those related models, it looks for fields of type AutomatedStorageTrackingField with the attribute
    `include_in_parents_count` set to True. For each such related child instance, it sums up the storage already
    calculated in its AutomatedStorageTrackingField.

    Args:
        instance (models.Model): The instance for which the child records' storage needs to be computed.

    Returns:
        int: The total storage consumed by the child records in bytes.

    Notes:
        - This function is not recursive. It only computes the storage for direct child objects,
          relying on each child object's AutomatedStorageTrackingField for its storage size.
        - The function only considers children connected through StorageAwareForeignKey fields with
          `count_as_storage_parent` set to True.
    """

    total_storage: int = 0

    for related_object in instance._meta.related_objects:
        related_model: models.Model = related_object.related_model
        related_name = related_object.get_accessor_name()

        if related_object.field and isinstance(
                related_object.field, StorageAwareForeignKey
        ) and related_object.field.count_as_storage_parent:
            try:
                for child_field in related_model._meta.fields:
                    if isinstance(child_field, AutomatedStorageTrackingField) and child_field.include_in_parents_count:
                        children = getattr(instance, related_name).all()
                        for child in children:
                            instance_storage: int = 0
                            for field in child._meta.fields:
                                if isinstance(field, AutomatedStorageTrackingField):
                                    instance_storage: int = getattr(child, field.name)
                                    break
                            total_storage += instance_storage
                        break
            except FieldDoesNotExist as e:
                print(f"getting field does not exist error as follows: {e}")
                continue
    return total_storage


# noinspection PyProtectedMember
def compute_external_storage(instance: models.Model) -> int:
    """
    Compute the storage reported by ExternalStorageTrackingFields of a given instance.

    Args:
        instance (Model): The instance for which external storage is to be computed.

    Returns:
        int: Total storage (in bytes) reported by the instance's ExternalStorageTrackingFields.
    """
    total_storage: int = 0
    for field in instance._meta.fields:
        if isinstance(field, ExternalStorageTrackingField):
            total_storage += getattr(instance, field.name, 0)
    return total_storage


# noinspection PyProtectedMember
def compute_file_fields_storage(instance: models.Model) -> int:
    """
    Compute the storage consumed by the file fields of a given instance.

    Args:
        instance (Model): The instance whose file fields' storage is to be computed.

    Returns:
        int: Total storage (in bytes) consumed by the file fields.
    """
    total_storage: int = 0

    for field in instance._meta.fields:
        if isinstance(field, (models.FileField, models.ImageField)):
            file_field: models.Field = getattr(instance, field.name)
            if file_field and file_field.file:
                try:
                    total_storage += file_field.file.size
                except Exception as e:
                    print(f"Error getting size for file field {field.name}: {e}")

    return total_storage


# noinspection PyProtectedMember
def notify_parents_to_recompute(instance: models.Model) -> None:
    """
    Notifies the parent records of a given instance to recompute their storage utilization.

    This function iterates through all fields of the given instance to identify any fields that are
    of type StorageAwareForeignKey and have the `count_as_storage_parent` attribute set to True.
    For each such field, the function identifies the parent record (the object referenced by the
    StorageAwareForeignKey) and invokes a save operation on it. The save operation triggers a
    re-computation of the parent's storage usage.

    Args:
        instance (models.Model): The child instance that may have one or more parents needing
        a storage re-computation.

    Note:
        This function assumes that the parent models have an AutomatedStorageTrackingField for
        tracking their storage utilization. A save operation on the parent model will initiate
        the re-computation of this field.
    """

    for field in instance._meta.fields:
        if isinstance(field, StorageAwareForeignKey) and field.count_as_storage_parent:
            for parent_field in field.related_model._meta.fields:
                if isinstance(parent_field, AutomatedStorageTrackingField):
                    parent: models.Model = getattr(instance, field.name)
                    parent.save()
                    break
