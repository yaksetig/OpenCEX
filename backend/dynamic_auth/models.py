"""
WalletAddress model for Dynamic wallet authentication.
Links blockchain wallet addresses to user accounts.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class WalletAddress(models.Model):
    """
    Links blockchain wallet addresses to user accounts.
    Supports multiple wallets per user for different EVM chains.
    """
    CHAIN_CHOICES = [
        ('eip155:1', 'Ethereum'),
        ('eip155:137', 'Polygon'),
        ('eip155:56', 'BSC'),
        ('eip155:42161', 'Arbitrum'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallet_addresses'
    )
    address = models.CharField(max_length=42, db_index=True)
    chain = models.CharField(
        max_length=32,
        choices=CHAIN_CHOICES,
        default='eip155:1'
    )
    is_primary = models.BooleanField(default=False)
    dynamic_user_id = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['address', 'chain']
        verbose_name = 'Wallet Address'
        verbose_name_plural = 'Wallet Addresses'

    def __str__(self):
        return f"{self.address[:8]}...{self.address[-6:]} ({self.get_chain_display()})"

    def save(self, *args, **kwargs):
        # Normalize EVM addresses to lowercase
        self.address = self.address.lower()

        # If this is set as primary, unset other primary wallets for this user
        if self.is_primary and self.user_id:
            WalletAddress.objects.filter(
                user_id=self.user_id,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)
