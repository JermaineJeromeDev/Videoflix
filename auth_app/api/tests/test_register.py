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
def register_url() -> str:
    """Return the endpoint URL for user registration."""
    return "/api/register/"


@pytest.mark.django_db
class TestRegisterHappyPath:
    """Contain all successful test scenarios for user registration."""

    def test_registration_success(
        self, api_client: APIClient, register_url: str
    ) -> None:
        """Verify that a valid user is created successfully as inactive."""
        payload = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "confirmed_password": "securepassword123",
        }
        response = api_client.post(register_url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "user" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"

        user = User.objects.get(email="newuser@example.com")
        assert user.is_active is False


@pytest.mark.django_db
class TestRegisterUnhappyPath:
    """Contain all failure and validation error scenarios for user registration."""

    def test_registration_password_mismatch(
        self, api_client: APIClient, register_url: str
    ) -> None:
        """Ensure mismatched passwords return a 400 error with a generic safety message."""
        payload = {
            "email": "mismatch@example.com",
            "password": "securepassword123",
            "confirmed_password": "wrongpassword123",
        }
        response = api_client.post(register_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_msg = str(response.data)
        assert "Bitte überprüfe deine Eingaben und versuche es erneut." in error_msg

    def test_registration_email_already_exists(
        self, api_client: APIClient, register_url: str
    ) -> None:
        """Ensure existing email registration fails with the identical generic safety message."""
        User.objects.create_user(email="existing@example.com", password="password123")

        payload = {
            "email": "existing@example.com",
            "password": "securepassword123",
            "confirmed_password": "securepassword123",
        }
        response = api_client.post(register_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_msg = str(response.data)
        assert "Bitte überprüfe deine Eingaben und versuche es erneut." in error_msg
