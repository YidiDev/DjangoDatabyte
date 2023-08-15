# noinspection PyProtectedMember
def compute_instance_storage(instance):
    """Compute the storage used by the instance based on the length of all its string fields."""
    total_storage = 0
    for field in instance._meta.fields:
        value = getattr(instance, field.name, None)
        if value and isinstance(value, str):
            total_storage += len(value)
    return total_storage


# noinspection PyProtectedMember
def compute_child_storage(instance):
    """Recursively compute storage used by child records."""
    total_storage = 0
    for related_object in instance._meta.related_objects:
        # Filter only those children with AutomatedStorageTrackingField and include_in_parents_count=True
        related_model = related_object.related_model
        if hasattr(
                related_model, 'AutomatedStorageTrackingField'
        ) and related_model.AutomatedStorageTrackingField.include_in_parents_count:
            related_name = related_object.get_accessor_name()
            children = getattr(instance, related_name).all()
            for child in children:
                total_storage += compute_instance_storage(child) + compute_child_storage(child)
    return total_storage
