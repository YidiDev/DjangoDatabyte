from django.db import models
from databyte.fields import ExternalStorageTrackingField, StorageAwareForeignKey


# noinspection PyProtectedMember,PyTypeChecker
def compute_instance_storage(instance: models.Model) -> int:
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
        elif isinstance(field, models.ForeignKey):
            total_storage += len(str(value.pk))
        else:
            total_storage += len(str(value).encode('utf-8'))
    return total_storage


# noinspection PyProtectedMember
def compute_child_storage(instance: models.Model) -> int:
    total_storage: int = 0
    for related_object in instance._meta.related_objects:
        related_model: models.Model = related_object.related_model
        related_name = related_object.get_accessor_name()
        field = instance._meta.get_field(related_name)
        if isinstance(field, StorageAwareForeignKey) and field.count_as_storage_parent:
            if hasattr(
                    related_model, 'AutomatedStorageTrackingField'
            ) and related_model.AutomatedStorageTrackingField.include_in_parents_count:
                children = getattr(instance, related_name).all()
                for child in children:
                    total_storage += compute_instance_storage(child) + compute_child_storage(child)
    return total_storage


# noinspection PyProtectedMember
def compute_external_storage(instance: models.Model) -> int:
    total_storage: int = 0
    for field in instance._meta.fields:
        if isinstance(field, ExternalStorageTrackingField):
            total_storage += getattr(instance, field.name, 0)
    return total_storage


# noinspection PyProtectedMember
def compute_file_fields_storage(instance: models.Model) -> int:
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
