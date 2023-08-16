from django.db import models

from databyte.fields import ExternalStorageTrackingField


# noinspection PyProtectedMember
def compute_instance_storage(instance: models.Model) -> int:
    """Compute the storage used by the instance based on the length of all its string fields."""
    total_storage: int = 0
    for field in instance._meta.fields:
        value: models.Field | None = getattr(instance, field.name, None)

        # If value is None, skip the field
        if value is None:
            total_storage += 1
            continue

        # For string fields (CharField, TextField, etc.)
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
            total_storage += len(value.encode('utf-8'))  # Using utf-8 as a general representation

        # For integer fields (PositiveIntegerField, BigIntegerField, etc.)
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
            total_storage += 8  # Typically, an integer uses 4-8 bytes

        # For boolean fields
        elif isinstance(field, models.BooleanField):
            total_storage += 1  # Typically, a boolean uses 1 byte

        # For date and time fields (DateField, TimeField, DateTimeField)
        elif isinstance(field, (models.DateField, models.TimeField, models.DateTimeField, models.DurationField)):
            total_storage += len(str(value).encode('utf-8'))

        # For float fields (FloatField, DecimalField)
        elif isinstance(field, (models.FloatField, models.DecimalField)):
            total_storage += 8  # Typically, a float uses 4-8 bytes

        # For binary data fields (BinaryField)
        elif isinstance(field, models.BinaryField):
            total_storage += len(value)

        # For UUID fields
        elif isinstance(field, models.UUIDField):
            total_storage += len(value.hex)

        elif isinstance(field, models.ForeignKey):
            total_storage += len(str(value.pk))

        # For other fields, use a generic approximation (this can be refined further)
        else:
            total_storage += len(str(value).encode('utf-8'))
    return total_storage


# noinspection PyProtectedMember
def compute_child_storage(instance: models.Model) -> int:
    """Recursively compute storage used by child records."""
    total_storage: int = 0
    for related_object in instance._meta.related_objects:
        # Filter only those children with AutomatedStorageTrackingField and include_in_parents_count=True
        related_model: models.Model = related_object.related_model
        if hasattr(
                related_model, 'AutomatedStorageTrackingField'
        ) and related_model.AutomatedStorageTrackingField.include_in_parents_count:
            related_name = related_object.get_accessor_name()
            children = getattr(instance, related_name).all()
            for child in children:
                total_storage += compute_instance_storage(child) + compute_child_storage(child)
    return total_storage


# noinspection PyProtectedMember
def compute_external_storage(instance: models.Model) -> int:
    """Compute the total of all ExternalStorageTrackingField fields on the instance."""
    total_storage: int = 0
    for field in instance._meta.fields:
        if isinstance(field, ExternalStorageTrackingField):
            total_storage += getattr(instance, field.name, 0)
    return total_storage


# noinspection PyProtectedMember
def compute_file_fields_storage(instance: models.Model) -> int:
    """
    Compute the storage used by file fields (FileField, ImageField) of the instance.
    """
    total_storage: int = 0

    for field in instance._meta.fields:
        # Check if the field is an instance of FileField or ImageField
        if isinstance(field, (models.FileField, models.ImageField)):
            file_field: models.Field = getattr(instance, field.name)
            if file_field and file_field.file:
                try:
                    # Get the file size from the storage backend
                    total_storage += file_field.file.size
                except Exception as e:
                    # Handle any errors that might occur while fetching the file size, e.g. file not found
                    print(f"Error getting size for file field {field.name}: {e}")

    return total_storage
