from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer
from .utils import generate_activation_token, send_activation_email


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
