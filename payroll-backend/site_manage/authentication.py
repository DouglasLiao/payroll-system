"""
Custom JWT Authentication Classes

This module provides custom JWT authentication that works with both:
1. Authorization header (standard JWT approach)
2. HttpOnly cookies (for browser-based clients)

This allows the backend to accept JWT tokens from either source,
providing flexibility and security.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads token from cookies OR Authorization header.

    This authenticator tries to read the JWT token from:
    1. Authorization header (Bearer <token>) - Standard approach
    2. access_token cookie - For httpOnly cookie-based auth

    This allows the same backend to work with:
    - Mobile apps / API clients (using Authorization header)
    - Browser apps (using httpOnly cookies for XSS protection)
    """

    def authenticate(self, request):
        # Try to get token from Authorization header first
        header = self.get_header(request)

        if header is not None:
            # Standard JWT authentication from header
            raw_token = self.get_raw_token(header)
        else:
            # Fallback to cookie
            raw_token = request.COOKIES.get("access_token")

        # If no token found in either location, return None (not authenticated)
        if raw_token is None:
            return None

        # Validate the token
        try:
            validated_token = self.get_validated_token(raw_token)
        except InvalidToken as e:
            # Token is invalid or expired
            raise AuthenticationFailed("Token inválido ou expirado") from e

        # Get user from validated token
        return self.get_user(validated_token), validated_token
