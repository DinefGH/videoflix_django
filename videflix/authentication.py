from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework.authtoken.models import Token

class CookieTokenAuthentication(BaseAuthentication):
    """
    Custom authentication class that authenticates users via a token stored in cookies.

    Methods:
        - authenticate(request):
            Attempts to retrieve the 'auth_token' from the request cookies. If a token is found,
            it validates the token and returns the associated user. If the token is invalid or
            does not exist, it raises an AuthenticationFailed exception or returns None.
    """
    def authenticate(self, request):
        """
        Authenticates the user based on the token in the 'auth_token' cookie.

        Args:
            request: The HTTP request containing the cookie.

        Returns:
            A tuple of (user, token) if the token is valid.
            None if no token is provided or the token is invalid.

        Raises:
            AuthenticationFailed: If the token is invalid.
        """
        token_key = request.COOKIES.get('auth_token')
        if not token_key:
            return None  # No authentication provided

        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (token.user, token)