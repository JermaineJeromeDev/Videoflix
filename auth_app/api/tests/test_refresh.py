import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Provide a fresh instance of the DRF APIClient."""
    return APIClient()


@pytest.fixture
def refresh_url() -> str:
    """Return the endpoint URL for token refreshing."""
    return "/api/token/refresh/"


@pytest.fixture
def create_active_user():
    """Fixture to create an active verified user."""
    user = User.objects.create_user(
        email="refreshuser@example.com", password="SecurePassword123"
    )
    user.is_active = True
    user.save()
    return user


@pytest.mark.django_db
class TestTokenRefreshHappyPath:
    """Contain successful test scenarios for token refreshing."""

    def test_token_refresh_success(
        self, api_client: APIClient, refresh_url: str, create_active_user
    ) -> None:
        """Verify that a valid refresh token cookie successfully issues a new access token cookie."""
        refresh = RefreshToken.for_user(create_active_user)
        api_client.cookies["refresh_token"] = str(refresh)

        response = api_client.post(refresh_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Token refreshed"
        assert "access" in response.data

        assert "access_token" in response.cookies
        assert response.cookies["access_token"]["httponly"] is True


@pytest.mark.django_db
class TestTokenRefreshUnhappyPath:
    """Contain failure scenarios for invalid refresh attempts."""

    def test_token_refresh_missing_cookie(
        self, api_client: APIClient, refresh_url: str
    ) -> None:
        """Ensure token refresh fails with 400 if the refresh token cookie is missing."""
        response = api_client.post(refresh_url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_refresh_invalid_cookie(
        self, api_client: APIClient, refresh_url: str
    ) -> None:
        """Ensure token refresh fails with 401 if the refresh token is invalid or altered."""
        api_client.cookies["refresh_token"] = "completely-invalid-token-string"

        response = api_client.post(refresh_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
