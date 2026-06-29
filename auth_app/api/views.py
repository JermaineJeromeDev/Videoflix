from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer
from .utils import (
    generate_activation_token,
    get_user_from_uidb64,
    send_activation_email,
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
