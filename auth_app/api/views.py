from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer
from .utils import (
    _get_auth_cookie_options,
    blacklist_refresh_token,
    generate_activation_token,
    get_tokens_for_user,
    get_user_from_uidb64,
    process_password_reset_request,
    refresh_access_token,
    reset_user_password,
    send_activation_email,
    set_auth_cookies,
    verify_and_activate_user,
)


class RegisterView(APIView):
    """API endpoint that allows new guests to register an account."""

    def post(self, request):
        """Handle incoming registration payloads and trigger activation workflow."""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = generate_activation_token(user)
            send_activation_email(user, token)

            return Response(
                {"user": {"id": user.id, "email": user.email}},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateView(APIView):
    """API endpoint to activate a user account using uidb64 and token."""

    def get(self, request, uidb64, token):
        """Validate activation parameters and activate the user profile."""
        user = get_user_from_uidb64(uidb64)
        if verify_and_activate_user(user, token):
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "Activation failed."}, status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """API endpoint to authenticate users and issue secure httpOnly cookies."""

    def post(self, request):
        """Verify user credentials, generate tokens, and set secure cookies."""
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, username=email, password=password)

        if user is None or not user.is_active:
            return Response(
                {"detail": "Bitte überprüfe deine Eingaben und versuche es erneut."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = get_tokens_for_user(user)
        response = Response(
            {
                "detail": "Login successful",
                "user": {"id": user.id, "username": user.email},
            },
            status=status.HTTP_200_OK,
        )

        set_auth_cookies(response, tokens, request=request)
        return response


class LogoutView(APIView):
    """API endpoint to log out users by blacklisting their refresh token."""

    def post(self, request):
        """Extract refresh token from cookies, blacklist it, and clear cookies."""

        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token or not blacklist_refresh_token(refresh_token):
            return Response(
                {"detail": "Refresh token is missing or invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(
            {
                "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class TokenRefreshView(APIView):
    """API endpoint to refresh the access token cookie using a refresh token cookie."""

    def post(self, request):
        """Extract refresh token from cookies and set a fresh access token cookie."""
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing"}, status=status.HTTP_400_BAD_REQUEST
            )

        new_access = refresh_access_token(refresh_token)
        if not new_access:
            return Response(
                {"detail": "Token invalid"}, status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response(
            {"detail": "Token refreshed", "access": new_access},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="access_token",
            value=new_access,
            **_get_auth_cookie_options(request=request)
        )
        return response


class PasswordResetRequestView(APIView):
    """API endpoint to initiate the password reset workflow."""

    def post(self, request):
        """Accept email payload and trigger asynchronous reset email if user exists."""
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        process_password_reset_request(email)

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK,
        )


class PasswordConfirmView(APIView):
    """API endpoint to confirm and finalize the password reset process."""

    def post(self, request, uidb64, token):
        """Validate input passwords and cryptographic tokens to update user credentials."""
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not new_password or new_password != confirm_password:
            return Response(
                {"detail": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_user_from_uidb64(uidb64)
        if reset_user_password(user, token, new_password):
            return Response(
                {"detail": "Your Password has been successfully reset."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST
        )
