"""
Databyte Application Initialization.

This module sets the default application configuration for the `databyte` application.
The configuration is set to the `DatabyteConfig` class located in the `apps.py` module of this application.

By setting the `default_app_config`, Django will use the specified app configuration
when setting up the application, ensuring the proper setup, especially for features like signals.
"""

default_app_config = 'databyte.apps.DatabyteConfig'
