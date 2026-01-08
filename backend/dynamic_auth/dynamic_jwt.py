"""
Dynamic XYZ JWT verification utility.
Verifies JWT tokens issued by Dynamic SDK using JWKS endpoint.
"""
import jwt
from jwt import PyJWKClient
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class DynamicJWTVerifier:
    """
    Verifies JWT tokens issued by Dynamic XYZ.
    Uses JWKS endpoint for RS256 signature verification.
    """

    def __init__(self):
        self._jwks_client = None

    @property
    def environment_id(self):
        return getattr(settings, 'DYNAMIC_ENVIRONMENT_ID', '')

    @property
    def jwks_url(self):
        return f"https://app.dynamic.xyz/api/v0/sdk/{self.environment_id}/.well-known/jwks"

    @property
    def jwks_client(self):
        """Lazy-load JWKS client with caching."""
        if self._jwks_client is None:
            self._jwks_client = PyJWKClient(
                self.jwks_url,
                cache_jwk_set=True,
                lifespan=getattr(settings, 'DYNAMIC_JWKS_CACHE_TTL', 600)
            )
        return self._jwks_client

    def verify_token(self, token: str) -> dict:
        """
        Verify a Dynamic JWT token and return decoded payload.

        Args:
            token: The JWT token string from Dynamic SDK

        Returns:
            dict: Decoded token payload containing user info

        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        if not self.environment_id:
            raise jwt.InvalidTokenError('DYNAMIC_ENVIRONMENT_ID not configured')

        try:
            # Get the signing key from JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            # Decode and verify the token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={
                    "verify_exp": True,
                    "verify_aud": False,  # Dynamic doesn't use audience claim
                    "require": ["exp", "iat", "sub"]
                }
            )

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Dynamic JWT token expired")
            raise
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid Dynamic JWT token: {e}")
            raise

    def extract_wallet_info(self, payload: dict) -> dict:
        """
        Extract wallet information from Dynamic JWT payload.

        Args:
            payload: Decoded JWT payload from verify_token()

        Returns:
            dict: Contains 'dynamic_user_id', 'email', 'wallets' list
        """
        verified_credentials = payload.get('verified_credentials', [])

        wallet_info = {
            'dynamic_user_id': payload.get('sub'),
            'email': payload.get('email'),
            'wallets': []
        }

        for cred in verified_credentials:
            if cred.get('format') == 'blockchain':
                wallet_info['wallets'].append({
                    'address': cred.get('address'),
                    'chain': cred.get('chain', 'eip155:1'),
                    'wallet_name': cred.get('wallet_name')
                })

        return wallet_info


# Singleton instance
dynamic_verifier = DynamicJWTVerifier()
