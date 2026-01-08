"""
Dynamic authentication settings.

These settings should be added to the Django project's settings.
This file serves as documentation and can be imported.
"""
import os

# Dynamic XYZ Configuration
DYNAMIC_ENVIRONMENT_ID = os.environ.get('DYNAMIC_ENVIRONMENT_ID', '')

# JWKS cache time-to-live in seconds (default: 10 minutes)
DYNAMIC_JWKS_CACHE_TTL = int(os.environ.get('DYNAMIC_JWKS_CACHE_TTL', 600))

# Settings to add to INSTALLED_APPS
DYNAMIC_AUTH_APP = 'dynamic_auth'

# Authentication class to add to DRF
DYNAMIC_AUTH_CLASS = 'dynamic_auth.authentication.DynamicWalletAuthentication'
