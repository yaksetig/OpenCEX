"""
Django admin configuration for Dynamic authentication models.
"""
from django.contrib import admin
from .models import WalletAddress


@admin.register(WalletAddress)
class WalletAddressAdmin(admin.ModelAdmin):
    list_display = ['address_short', 'user', 'chain', 'is_primary', 'created_at']
    list_filter = ['chain', 'is_primary', 'created_at']
    search_fields = ['address', 'user__email', 'user__username', 'dynamic_user_id']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    def address_short(self, obj):
        return f"{obj.address[:8]}...{obj.address[-6:]}"
    address_short.short_description = 'Address'
