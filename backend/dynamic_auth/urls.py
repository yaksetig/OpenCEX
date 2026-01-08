"""
URL configuration for Dynamic wallet authentication.
"""
from django.urls import path
from .views import DynamicAuthView, LinkWalletView, UserWalletsView

app_name = 'dynamic_auth'

urlpatterns = [
    path('dynamic/', DynamicAuthView.as_view(), name='dynamic-auth'),
    path('link-wallet/', LinkWalletView.as_view(), name='link-wallet'),
    path('wallets/', UserWalletsView.as_view(), name='user-wallets'),
]
