from django.db import models


class StorageAwareForeignKey(models.ForeignKey):
    """
    A custom ForeignKey field that is aware of storage tracking requirements.

    Attributes:
        count_as_storage_parent (bool): If set to True, this ForeignKey will
        be treated as a storage parent in the tracking hierarchy.
    """

    def __init__(self, *args, count_as_storage_parent: bool = False, **kwargs):
        """
        Initializes the StorageAwareForeignKey.

        Args:
            count_as_storage_parent (bool, optional): Indicates whether this ForeignKey
            should be treated as a storage parent. Defaults to False.
        """
        self.count_as_storage_parent: bool = count_as_storage_parent
        super().__init__(*args, **kwargs)


class ExternalStorageTrackingField(models.BigIntegerField):
    """
    A custom field that represents storage that is tracked externally.

    This field extends the BigIntegerField with a default value of 0, indicating
    that the initial external storage consumed is 0 by default.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the ExternalStorageTrackingField with a default value of 0.
        """
        kwargs['default'] = 0
        super().__init__(*args, **kwargs)


class AutomatedStorageTrackingField(models.BigIntegerField):
    """
    A custom field that represents storage that is tracked automatically.

    This field extends the BigIntegerField. The field can be flagged to
    include its storage count in its parent's count.

    Attributes:
        include_in_parents_count (bool): If set to True, the storage used by this
        field will be added to its parent's storage count.
    """

    def __init__(self, include_in_parents_count: bool = False, *args, **kwargs):
        """
        Initializes the AutomatedStorageTrackingField.

        Args:
            include_in_parents_count (bool, optional): Indicates whether the storage used
            by this field should be added to its parent's storage count. Defaults to False.
        """
        self.include_in_parents_count: bool = include_in_parents_count
        kwargs['default'] = 0
        super().__init__(*args, **kwargs)
        