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
def create_active_user():
    """Fixture to create an active verified user."""
    user = User.objects.create_user(
        email="confirmme@example.com", password="OldSecurePassword123"
    )
    user.is_active = True
    user.save()
    return user


@pytest.mark.django_db
class TestPasswordConfirmHappyPath:
    """Contain successful test scenarios for password confirmation."""

    def test_password_confirm_success(
        self, api_client: APIClient, create_active_user
    ) -> None:
        """Verify that valid parameters successfully change the user's password."""
        user = create_active_user
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        url = f"/api/password_confirm/{uidb64}/{token}/"
        payload = {
            "new_password": "NewSecurePassword123",
            "confirm_password": "NewSecurePassword123",
        }
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Your Password has been successfully reset."

        user.refresh_from_db()
        assert user.check_password("NewSecurePassword123") is True


@pytest.mark.django_db
class TestPasswordConfirmUnhappyPath:
    """Contain failure scenarios for invalid password confirmation attempts."""

    def test_confirm_password_mismatch(
        self, api_client: APIClient, create_active_user
    ) -> None:
        """Ensure that mismatched passwords return a 400 error."""
        user = create_active_user
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        url = f"/api/password_confirm/{uidb64}/{token}/"
        payload = {
            "new_password": "NewSecurePassword123",
            "confirm_password": "MismatchedPassword123",
        }
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_confirm_invalid_token(
        self, api_client: APIClient, create_active_user
    ) -> None:
        """Ensure that an invalid token is rejected with a 400 error."""
        user = create_active_user
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = "completely-invalid-token"

        url = f"/api/password_confirm/{uidb64}/{invalid_token}/"
        payload = {
            "new_password": "NewSecurePassword123",
            "confirm_password": "NewSecurePassword123",
        }
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
