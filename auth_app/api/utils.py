from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

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
