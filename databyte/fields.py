from django.db import models


class StorageAwareForeignKey(models.ForeignKey):
    def __init__(self, *args, count_as_storage_parent=False, **kwargs):
        self.count_as_storage_parent = count_as_storage_parent
        super().__init__(*args, **kwargs)


class ExternalStorageTrackingField(models.BigIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['default'] = 0
        super().__init__(*args, **kwargs)


class AutomatedStorageTrackingField(models.BigIntegerField):
    def __init__(self, include_in_parents_count: bool = False, *args, **kwargs):
        self.include_in_parents_count: bool = include_in_parents_count
        kwargs['default'] = 0
        super().__init__(*args, **kwargs)
