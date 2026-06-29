import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Provide a fresh instance of the DRF APIClient."""
    return APIClient()


@pytest.fixture
def create_inactive_user():
    """Fixture to create a sample inactive user."""
    return User.objects.create_user(
        email="activate_test@example.com", password="SecurePassword123"
    )


@pytest.mark.django_db
class TestActivationHappyPath:
    """Contain all successful test scenarios for user account activation."""

    def test_activation_success(
        self, api_client: APIClient, create_inactive_user
    ) -> None:
        """Verify that a valid uidb64 and token successfully activate the account."""
        user = create_inactive_user
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        url = f"/api/activate/{uidb64}/{token}/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Account successfully activated."

        user.refresh_from_db()
        assert user.is_active is True


@pytest.mark.django_db
class TestActivationUnhappyPath:
    """Contain all failure and validation error scenarios for account activation."""

    def test_activation_invalid_token(
        self, api_client: APIClient, create_inactive_user
    ) -> None:
        """Ensure that an incorrect token returns a 400 error and keeps user inactive."""
        user = create_inactive_user
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = "completely-invalid-token"

        url = f"/api/activate/{uidb64}/{invalid_token}/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.is_active is False

    def test_activation_invalid_uidb64(
        self, api_client: APIClient, create_inactive_user
    ) -> None:
        """Ensure that an invalid or altered uidb64 returns a 400 error."""
        user = create_inactive_user
        token = default_token_generator.make_token(user)
        invalid_uidb64 = "invalidUid64"

        url = f"/api/activate/{invalid_uidb64}/{token}/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
