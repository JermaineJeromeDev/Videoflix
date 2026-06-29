from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer
from .utils import (
    blacklist_refresh_token,
    generate_activation_token,
    get_tokens_for_user,
    get_user_from_uidb64,
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
                {"user": {"id": user.id, "email": user.email}, "token": token},
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

        set_auth_cookies(response, tokens)
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
