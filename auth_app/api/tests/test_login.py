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
def login_url() -> str:
    """Return the endpoint URL for user login."""
    return "/api/login/"


@pytest.fixture
def create_active_user():
    """Fixture to create a verified active test user."""
    user = User.objects.create_user(
        email="activeuser@example.com", password="SecurePassword123"
    )
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def create_inactive_user():
    """Fixture to create an unverified inactive test user."""
    return User.objects.create_user(
        email="inactiveuser@example.com", password="SecurePassword123"
    )


@pytest.mark.django_db
class TestLoginHappyPath:
    """Contain all successful test scenarios for user authentication."""

    def test_login_success(
        self, api_client: APIClient, login_url: str, create_active_user
    ) -> None:
        """Verify that valid credentials return success response and set secure HttpOnly cookies."""
        payload = {"email": "activeuser@example.com", "password": "SecurePassword123"}
        response = api_client.post(login_url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Login successful"
        assert response.data["user"]["username"] == "activeuser@example.com"

        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        assert response.cookies["access_token"]["httponly"] is True
        assert response.cookies["refresh_token"]["httponly"] is True


@pytest.mark.django_db
class TestLoginUnhappyPath:
    """Contain all failure and validation error scenarios for user authentication."""

    def test_login_wrong_credentials(
        self, api_client: APIClient, login_url: str, create_active_user
    ) -> None:
        """Ensure incorrect passwords trigger a 401 response and don't issue any auth cookies."""
        payload = {"email": "activeuser@example.com", "password": "WrongPassword123"}
        response = api_client.post(login_url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access_token" not in response.cookies

        error_msg = str(response.data)
        assert "Bitte überprüfe deine Eingaben und versuche es erneut." in error_msg

    def test_login_inactive_account(
        self, api_client: APIClient, login_url: str, create_inactive_user
    ) -> None:
        """Ensure unverified or inactive accounts cannot log in and trigger an error response."""
        payload = {"email": "inactiveuser@example.com", "password": "SecurePassword123"}
        response = api_client.post(login_url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access_token" not in response.cookies

        error_msg = str(response.data)
        assert "Bitte überprüfe deine Eingaben und versuche es erneut." in error_msg
