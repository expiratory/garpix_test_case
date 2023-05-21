"""
ApiConfig
"""


from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    ApiConfig for Photos
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Photos'
