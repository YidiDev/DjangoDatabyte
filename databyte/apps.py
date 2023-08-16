from django.apps import AppConfig


class DatabyteConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'databyte'
    verbose_name: str = 'Databyte'
