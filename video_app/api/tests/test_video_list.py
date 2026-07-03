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
def video_url() -> str:
    """Return the endpoint URL for retrieving the video list."""
    return "/api/video/"


@pytest.fixture
def authenticated_client(api_client) -> APIClient:
    """Provide a client pre-authenticated with secure session cookies."""
    user = User.objects.create_user(email="viewer@example.com", password="Password123")
    user.is_active = True
    user.save()
    refresh = RefreshToken.for_user(user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    return api_client


@pytest.mark.django_db
class TestVideoListHappyPath:
    """Contain successful test scenarios for fetching the video list."""

    def test_get_video_list_success_and_order(
        self, authenticated_client: APIClient, video_url: str
    ) -> None:
        """Verify that authenticated users can fetch videos sorted by creation date DESC."""

        from django.apps import apps

        Video = apps.get_model("video_app", "Video")

        v1 = Video.objects.create(
            title="Older Movie", description="Desc", category="Drama"
        )
        v2 = Video.objects.create(
            title="Newer Movie", description="Desc", category="Romance"
        )

        response = authenticated_client.get(video_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        assert response.data[0]["id"] == v2.id
        assert response.data[1]["id"] == v1.id


@pytest.mark.django_db
class TestVideoListUnhappyPath:
    """Contain failure scenarios for fetching the video list."""

    def test_get_video_list_unauthenticated(
        self, api_client: APIClient, video_url: str
    ) -> None:
        """Ensure that requests without proper auth cookies are rejected with a 401 error."""
        response = api_client.get(video_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
