from django.contrib.auth.tokens import default_token_generator


def generate_activation_token(user):
    """Generate a secure cryptographic token for user activation."""
    return default_token_generator.make_token(user)


def send_activation_email(user, token):
    """Send an activation email containing the verification link."""
    pass
