from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from video_app.api.authentication import CookieJWTAuthentication
from video_app.api.serializers import VideoSerializer
from video_app.models import Video

from .utils import get_hls_manifest_file, get_hls_segment_file


class VideoListView(APIView):
    """API endpoint to retrieve all available videos ordered by creation date DESC."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return serialized video list sorted newest first with request context."""
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class HLSManifestView(APIView):
    """API endpoint to stream secure HLS .m3u8 playlists."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """Open and return the requested m3u8 file as a secure FileResponse."""
        file_path = get_hls_manifest_file(movie_id, resolution)
        if not file_path:
            raise Http404("Manifest file not found.")

        file_handle = open(file_path, "rb")
        return FileResponse(file_handle, content_type="application/vnd.apple.mpegurl")


class HLSSegmentView(APIView):
    """API endpoint to stream secure bin HLS .ts video segments."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Open and return the requested ts file as a secure FileResponse."""
        file_path = get_hls_segment_file(movie_id, resolution, segment)
        if not file_path:
            raise Http404("Segment file not found.")

        file_handle = open(file_path, "rb")
        return FileResponse(file_handle, content_type="video/MP2T")
