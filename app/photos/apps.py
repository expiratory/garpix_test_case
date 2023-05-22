"""
ApiConfig
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    ApiConfig for photos
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'photos'
