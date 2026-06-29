import pytest
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from video_app.models import Video

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Provide a fresh instance of the DRF APIClient."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client) -> APIClient:
    """Provide a client pre-authenticated with secure session cookies."""
    user = User.objects.create_user(email="player@example.com", password="Password123")
    user.is_active = True
    user.save()
    refresh = RefreshToken.for_user(user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    return api_client


@pytest.fixture
def create_test_video():
    """Fixture to create a video in the database."""
    return Video.objects.create(
        title="Segment Movie", description="Desc", category="Sci-Fi"
    )


@pytest.mark.django_db
class TestHLSSegmentsHappyPath:
    """Contain successful test scenarios for HLS segment streaming."""

    def test_get_ts_segment_success(
        self, authenticated_client: APIClient, create_test_video
    ) -> None:
        """Verify that authenticated users can fetch a valid ts segment file."""
        video = create_test_video
        segment_path = f"videos/{video.id}/720p/000.ts"
        default_storage.save(segment_path, ContentFile(b"binaryvideodata"))

        url = f"/api/video/{video.id}/720p/000.ts/"
        response = authenticated_client.get(url)

        if default_storage.exists(segment_path):
            default_storage.delete(segment_path)

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "video/MP2T"


@pytest.mark.django_db
class TestHLSSegmentsUnhappyPath:
    """Contain failure scenarios for HLS segment streaming."""

    def test_get_ts_segment_unauthenticated(
        self, api_client: APIClient, create_test_video
    ) -> None:
        """Ensure unauthenticated requests are rejected with a 401 error."""
        video = create_test_video
        url = f"/api/video/{video.id}/720p/000.ts/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_ts_segment_not_found(
        self, authenticated_client: APIClient, create_test_video
    ) -> None:
        """Ensure missing segments return a 404 error."""
        video = create_test_video
        url = f"/api/video/{video.id}/720p/999.ts/"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
