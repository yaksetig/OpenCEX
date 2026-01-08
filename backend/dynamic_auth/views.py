"""
API views for Dynamic wallet authentication.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction
import jwt
import logging

from .dynamic_jwt import dynamic_verifier
from .models import WalletAddress

logger = logging.getLogger(__name__)
User = get_user_model()


class DynamicAuthThrottle(AnonRateThrottle):
    """Rate limit Dynamic auth endpoint to prevent abuse."""
    rate = '20/minute'


class DynamicAuthView(APIView):
    """
    Authenticate user with Dynamic wallet token.

    POST /api/auth/dynamic/
    Body: { "token": "<dynamic_jwt_token>" }

    Returns: OpenCEX JWT tokens (access + refresh)

    This endpoint:
    1. Verifies the Dynamic JWT token against JWKS
    2. Extracts wallet address and email from the token
    3. Finds existing user or creates a new one
    4. Returns OpenCEX JWT tokens for API access
    """
    permission_classes = [AllowAny]
    throttle_classes = [DynamicAuthThrottle]

    def post(self, request):
        dynamic_token = request.data.get('token')

        if not dynamic_token:
            return Response(
                {'error': 'Dynamic token required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify Dynamic token
            payload = dynamic_verifier.verify_token(dynamic_token)
            wallet_info = dynamic_verifier.extract_wallet_info(payload)

            if not wallet_info['wallets']:
                return Response(
                    {'error': 'No wallet found in token'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            primary_wallet = wallet_info['wallets'][0]

            # Find or create user
            user = self._get_or_create_user(wallet_info, primary_wallet)

            # Generate OpenCEX JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'wallet_address': primary_wallet['address'],
                }
            })

        except jwt.InvalidTokenError as e:
            logger.warning(f"Dynamic auth failed: {e}")
            return Response(
                {'error': f'Invalid token: {str(e)}'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    @transaction.atomic
    def _get_or_create_user(self, wallet_info: dict, primary_wallet: dict) -> User:
        """Find existing user or create new one."""
        address = primary_wallet['address'].lower()
        chain = primary_wallet.get('chain', 'eip155:1')

        # Try to find by wallet
        try:
            wallet = WalletAddress.objects.select_related('user').get(
                address=address,
                chain=chain
            )
            # Update dynamic_user_id if changed
            dynamic_user_id = wallet_info.get('dynamic_user_id')
            if dynamic_user_id and wallet.dynamic_user_id != dynamic_user_id:
                wallet.dynamic_user_id = dynamic_user_id
                wallet.save(update_fields=['dynamic_user_id'])
            return wallet.user
        except WalletAddress.DoesNotExist:
            pass

        # Try to find by Dynamic user ID (for users who connected different wallet)
        dynamic_user_id = wallet_info.get('dynamic_user_id')
        if dynamic_user_id:
            existing_wallet = WalletAddress.objects.filter(
                dynamic_user_id=dynamic_user_id
            ).select_related('user').first()
            if existing_wallet:
                # Add this new wallet to existing user
                WalletAddress.objects.create(
                    user=existing_wallet.user,
                    address=address,
                    chain=chain,
                    is_primary=False,
                    dynamic_user_id=dynamic_user_id
                )
                return existing_wallet.user

        # Create new user
        email = wallet_info.get('email') or f"{address[:10]}@wallet.opencex"
        username = f"wallet_{address[:16]}"

        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=None  # No password for wallet-only users
        )

        # Create wallet address record
        WalletAddress.objects.create(
            user=user,
            address=address,
            chain=chain,
            is_primary=True,
            dynamic_user_id=dynamic_user_id
        )

        # Create profile if Profile model exists
        try:
            from core.models.facade import Profile
            Profile.objects.get_or_create(user=user)
        except ImportError:
            logger.warning("Profile model not found, skipping profile creation")

        logger.info(f"Created new wallet user: {username} with address {address}")
        return user


class LinkWalletView(APIView):
    """
    Link a wallet to existing authenticated user.

    POST /api/auth/link-wallet/
    Body: { "token": "<dynamic_jwt_token>" }

    Allows authenticated users to add additional wallet addresses.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        dynamic_token = request.data.get('token')

        if not dynamic_token:
            return Response(
                {'error': 'Dynamic token required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payload = dynamic_verifier.verify_token(dynamic_token)
            wallet_info = dynamic_verifier.extract_wallet_info(payload)

            if not wallet_info['wallets']:
                return Response(
                    {'error': 'No wallet found in token'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            linked_wallets = []

            for wallet_data in wallet_info['wallets']:
                address = wallet_data['address'].lower()
                chain = wallet_data.get('chain', 'eip155:1')

                # Check if wallet already linked to another user
                existing = WalletAddress.objects.filter(
                    address=address,
                    chain=chain
                ).exclude(user=request.user).first()

                if existing:
                    return Response(
                        {'error': f'Wallet {address[:8]}... already linked to another account'},
                        status=status.HTTP_409_CONFLICT
                    )

                # Create or update wallet link
                wallet, created = WalletAddress.objects.update_or_create(
                    address=address,
                    chain=chain,
                    defaults={
                        'user': request.user,
                        'dynamic_user_id': wallet_info.get('dynamic_user_id')
                    }
                )

                linked_wallets.append({
                    'address': address,
                    'chain': chain,
                    'is_new': created
                })

            return Response({
                'message': 'Wallet linked successfully',
                'wallets': linked_wallets
            })

        except jwt.InvalidTokenError as e:
            return Response(
                {'error': f'Invalid token: {str(e)}'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserWalletsView(APIView):
    """
    Get all wallets linked to the authenticated user.

    GET /api/auth/wallets/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallets = WalletAddress.objects.filter(user=request.user).order_by('-is_primary', '-created_at')
        return Response({
            'wallets': [
                {
                    'address': w.address,
                    'chain': w.chain,
                    'chain_name': w.get_chain_display(),
                    'is_primary': w.is_primary,
                    'created_at': w.created_at.isoformat()
                }
                for w in wallets
            ]
        })

    def delete(self, request):
        """
        Remove a wallet from the user's account.

        DELETE /api/auth/wallets/
        Body: { "address": "0x...", "chain": "eip155:1" }
        """
        address = request.data.get('address', '').lower()
        chain = request.data.get('chain', 'eip155:1')

        if not address:
            return Response(
                {'error': 'Wallet address required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Don't allow removing the last wallet
        wallet_count = WalletAddress.objects.filter(user=request.user).count()
        if wallet_count <= 1:
            return Response(
                {'error': 'Cannot remove last wallet. Account must have at least one wallet.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            wallet = WalletAddress.objects.get(
                user=request.user,
                address=address,
                chain=chain
            )
            was_primary = wallet.is_primary
            wallet.delete()

            # If deleted wallet was primary, make another one primary
            if was_primary:
                new_primary = WalletAddress.objects.filter(user=request.user).first()
                if new_primary:
                    new_primary.is_primary = True
                    new_primary.save(update_fields=['is_primary'])

            return Response({'message': 'Wallet removed successfully'})

        except WalletAddress.DoesNotExist:
            return Response(
                {'error': 'Wallet not found'},
                status=status.HTTP_404_NOT_FOUND
            )
