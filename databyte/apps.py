from django.apps import AppConfig


# noinspection PyUnresolvedReferences
class DatabyteConfig(AppConfig):
    """
    AppConfig for the Databyte application.

    This class is responsible for configuration details and metadata for the Databyte application.
    Upon initialization of the application, it imports the signals module to ensure that
    the signals are properly registered.

    Attributes:
        default_auto_field (str): The default auto field type to use for automatically
                                  generated primary keys.
        name (str): The name of the application.
        verbose_name (str): The human-readable verbose name for the application.
    """

    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'databyte'
    verbose_name: str = 'Databyte'

    def ready(self) -> None:
        """
        Override this method to perform initialization tasks such as registering signals.

        This method is called once at the beginning when Django starts, ensuring the setup
        of the application, especially for features like signals.
        """
        from . import signals
