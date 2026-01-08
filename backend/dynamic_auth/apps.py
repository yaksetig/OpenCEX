"""
Django app configuration for Dynamic authentication.
"""
from django.apps import AppConfig


class DynamicAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dynamic_auth'
    verbose_name = 'Dynamic Wallet Authentication'
