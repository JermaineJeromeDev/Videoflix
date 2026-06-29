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
def create_active_user():
    """Fixture to create an active verified user."""
    user = User.objects.create_user(
        email="logoutuser@example.com", password="SecurePassword123"
    )
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def authenticated_client(api_client, create_active_user):
    """Fixture to provide a client with active session cookies."""
    refresh = RefreshToken.for_user(create_active_user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    api_client.cookies["refresh_token"] = str(refresh)
    return api_client


@pytest.mark.django_db
class TestLogoutHappyPath:
    """Contain successful test scenarios for user logout."""

    def test_logout_success(self, authenticated_client: APIClient) -> None:
        """Verify that a valid refresh token cookie successfully logs out the user."""
        response = authenticated_client.post("/api/logout/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == (
            "Logout successful! All tokens will be deleted. Refresh token is now invalid."
        )

        assert response.cookies["access_token"].value == ""
        assert response.cookies["refresh_token"].value == ""


@pytest.mark.django_db
class TestLogoutUnhappyPath:
    """Contain failure scenarios for invalid logout attempts."""

    def test_logout_missing_cookie(self, api_client: APIClient) -> None:
        """Ensure logout fails with 400 if the refresh token cookie is missing."""
        response = api_client.post("/api/logout/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data
