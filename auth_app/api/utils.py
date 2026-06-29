from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

User = get_user_model()


def generate_activation_token(user):
    """Generate a secure cryptographic token for user activation."""
    return default_token_generator.make_token(user)


def send_activation_email(user, token):
    """Send an activation email containing the verification link."""
    pass


def get_user_from_uidb64(uidb64):
    """Decode uidb64 and return the corresponding user instance or None."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def verify_and_activate_user(user, token):
    """Check if the token is valid for the user and activate the account."""
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return True
    return False


def get_tokens_for_user(user):
    """Generate access and refresh tokens for a given user."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_auth_cookies(response, tokens):
    """Set secure HttpOnly cookies for access and refresh tokens."""
    response.set_cookie(
        key="access_token", value=tokens["access"], httponly=True, samesite="Lax"
    )
    response.set_cookie(
        key="refresh_token", value=tokens["refresh"], httponly=True, samesite="Lax"
    )


def blacklist_refresh_token(token_string):
    """Validate the refresh token string and add it to the blacklist."""
    try:
        token = RefreshToken(token_string)
        token.blacklist()
        return True
    except TokenError:
        return False
