import os

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
    user = User.objects.create_user(
        email="streamer@example.com", password="Password123"
    )
    user.is_active = True
    user.save()
    refresh = RefreshToken.for_user(user)
    api_client.cookies["access_token"] = str(refresh.access_token)
    return api_client


@pytest.fixture
def create_test_video():
    """Fixture to create a video in the database."""
    return Video.objects.create(
        title="Test Movie", description="Desc", category="Action"
    )


@pytest.mark.django_db
class TestHLSMasterPlaylistHappyPath:
    """Contain successful test scenarios for HLS playlist streaming."""

    def test_get_m3u8_manifest_success(
        self, authenticated_client: APIClient, create_test_video
    ) -> None:
        """Verify that authenticated users can fetch a valid m3u8 file."""
        video = create_test_video

        # Simulate a generated HLS file in the media folder path
        manifest_path = f"videos/{video.id}/480p/index.m3u8"
        default_storage.save(manifest_path, ContentFile("#EXTM3U\n#EXT-X-VERSION:3"))

        url = f"/api/video/{video.id}/480p/index.m3u8"
        response = authenticated_client.get(url)

        # Clean up simulated file afterwards
        if default_storage.exists(manifest_path):
            default_storage.delete(manifest_path)

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "application/vnd.apple.mpegurl"


@pytest.mark.django_db
class TestHLSMasterPlaylistUnhappyPath:
    """Contain failure scenarios for HLS playlist streaming."""

    def test_get_m3u8_unauthenticated(
        self, api_client: APIClient, create_test_video
    ) -> None:
        """Ensure unauthenticated requests are rejected with 401."""
        video = create_test_video
        url = f"/api/video/{video.id}/480p/index.m3u8"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_m3u8_not_found(
        self, authenticated_client: APIClient, create_test_video
    ) -> None:
        """Ensure missing resolution or video paths return a 404 error."""
        video = create_test_video
        url = f"/api/video/{video.id}/1080p/index.m3u8"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
