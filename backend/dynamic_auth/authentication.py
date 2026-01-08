"""
Django REST Framework authentication backend for Dynamic wallet tokens.
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import jwt
import logging

from .dynamic_jwt import dynamic_verifier
from .models import WalletAddress

logger = logging.getLogger(__name__)
User = get_user_model()


class DynamicWalletAuthentication(BaseAuthentication):
    """
    DRF Authentication backend for Dynamic wallet tokens.

    Expects Authorization header: Bearer <dynamic_jwt_token>

    This backend verifies the Dynamic JWT token against the JWKS endpoint
    and looks up the user by their wallet address.
    """

    keyword = 'Bearer'

    def authenticate(self, request):
        """
        Authenticate the request and return a tuple of (user, payload) or None.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith(f'{self.keyword} '):
            return None  # Let other auth backends handle

        token = auth_header[len(self.keyword) + 1:]

        # Check if this looks like a Dynamic token (they have specific structure)
        # Dynamic tokens are RS256 JWTs, while OpenCEX tokens are HS512
        try:
            # Peek at the header to determine token type
            unverified_header = jwt.get_unverified_header(token)
            if unverified_header.get('alg') != 'RS256':
                return None  # Not a Dynamic token, let other backends handle
        except jwt.exceptions.DecodeError:
            return None

        try:
            payload = dynamic_verifier.verify_token(token)
            wallet_info = dynamic_verifier.extract_wallet_info(payload)

            user = self._get_user_by_wallet(wallet_info)

            if user is None:
                raise AuthenticationFailed(
                    'User not registered. Please complete registration via /api/auth/dynamic/'
                )

            return (user, payload)

        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid Dynamic token: {str(e)}')

    def _get_user_by_wallet(self, wallet_info: dict):
        """
        Find existing user by wallet address or Dynamic user ID.

        Args:
            wallet_info: Dict with 'wallets' list and 'dynamic_user_id'

        Returns:
            User instance or None if not found
        """
        primary_wallet = wallet_info['wallets'][0] if wallet_info['wallets'] else None

        if not primary_wallet:
            return None

        # Try to find user by wallet address
        try:
            wallet = WalletAddress.objects.select_related('user').get(
                address=primary_wallet['address'].lower(),
                chain=primary_wallet.get('chain', 'eip155:1')
            )
            return wallet.user
        except WalletAddress.DoesNotExist:
            pass

        # Try to find by Dynamic user ID
        dynamic_user_id = wallet_info.get('dynamic_user_id')
        if dynamic_user_id:
            wallet = WalletAddress.objects.filter(
                dynamic_user_id=dynamic_user_id
            ).select_related('user').first()
            if wallet:
                return wallet.user

        return None

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return self.keyword
