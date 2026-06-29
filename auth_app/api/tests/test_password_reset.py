import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Provide a fresh instance of the DRF APIClient."""
    return APIClient()


@pytest.fixture
def password_reset_url() -> str:
    """Return the endpoint URL for initiating a password reset."""
    return "/api/password_reset/"


@pytest.fixture
def create_active_user():
    """Fixture to create an active verified user."""
    user = User.objects.create_user(
        email="resetme@example.com", password="SecurePassword123"
    )
    user.is_active = True
    user.save()
    return user


@pytest.mark.django_db
class TestPasswordResetInitiation:
    """Contain scenarios for initiating a password reset request."""

    def test_reset_existing_email(
        self, api_client: APIClient, password_reset_url: str, create_active_user
    ) -> None:
        """Verify that an existing email returns 200 and the correct success message."""
        payload = {"email": "resetme@example.com"}
        response = api_client.post(password_reset_url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["detail"] == "An email has been sent to reset your password."
        )

    def test_reset_non_existing_email(
        self, api_client: APIClient, password_reset_url: str
    ) -> None:
        """Ensure a non-existing email returns the identical 200 response for anonymity."""
        payload = {"email": "ghost@example.com"}
        response = api_client.post(password_reset_url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["detail"] == "An email has been sent to reset your password."
        )
