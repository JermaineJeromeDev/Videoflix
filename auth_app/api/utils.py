import os
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_rq import job
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

User = get_user_model()


def generate_activation_token(user):
    """Generate a secure cryptographic token for user activation."""
    return default_token_generator.make_token(user)


def send_activation_email(user, token):
    """Render the HTML activation template and queue the background task."""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    frontend_link = f"{settings.FRONTEND_URL.rstrip('/')}/pages/auth/activate.html?uid={uidb64}&token={token}"
    site_url = settings.BACKEND_URL.rstrip("/")

    context = {
        "user": user,
        "activate_url": frontend_link,
        "site_url": site_url,
    }
    html_content = render_to_string("auth_app/activation_email.html", context)
    text_content = strip_tags(html_content)

    send_async_email.delay(
        "Activate your Videoflix Account",
        text_content,
        [user.email],
        html_message=html_content,
    )


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


def refresh_access_token(refresh_token_string):
    """Validate refresh token and return a new access token string or None."""
    try:
        refresh = RefreshToken(refresh_token_string)
        return str(refresh.access_token)
    except Exception:
        return None


def send_password_reset_email(user, token):
    """Render the HTML password reset template and queue the background task."""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    frontend_link = f"{settings.FRONTEND_URL.rstrip('/')}/pages/auth/password_confirm.html?uid={uidb64}&token={token}"
    site_url = settings.BACKEND_URL.rstrip("/")

    context = {
        "user": user,
        "reset_url": frontend_link,
        "site_url": site_url,
    }
    html_content = render_to_string("auth_app/password_reset_email.html", context)
    text_content = strip_tags(html_content)

    send_async_email.delay(
        "Passwort zurücksetzen bei Videoflix",
        text_content,
        [user.email],
        html_message=html_content,
    )


def process_password_reset_request(email):
    """Generate uidb64 and password reset token if the user exists."""
    try:
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        send_password_reset_email(user, token)
        return True
    except User.DoesNotExist:
        return False


def reset_user_password(user, token, new_password):
    """Verify the token and update the user's password securely."""
    if user and default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return True
    return False


@job
def send_async_email(subject, message, recipient_list, html_message=None):
    """Send a secure development email asynchronously via background worker."""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
        html_message=html_message,
    )
