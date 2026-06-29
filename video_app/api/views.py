from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from video_app.api.authentication import CookieJWTAuthentication
from video_app.api.serializers import VideoSerializer
from video_app.models import Video


class VideoListView(ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
