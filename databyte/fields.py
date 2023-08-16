from django.db import models


class ExternalStorageTrackingField(models.BigIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['default'] = 0
        super().__init__(*args, **kwargs)


class AutomatedStorageTrackingField(models.BigIntegerField):
    def __init__(self, include_in_parents_count: bool = False, *args, **kwargs):
        self.include_in_parents_count: bool = include_in_parents_count
        kwargs['default'] = 0
        super().__init__(*args, **kwargs)