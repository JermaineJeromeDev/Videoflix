from django.urls import path

from .views import HLSManifestView, VideoListView

urlpatterns = [
    path("video/", VideoListView.as_view(), name="video_list"),
    path(
        "video/<int:movie_id>/<str:resolution>/index.m3u8",
        HLSManifestView.as_view(),
        name="hls_manifest",
    ),
]
