from django.conf import settings
from rest_framework import serializers

from ..models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializer to map the Video model instance and generate absolute thumbnail URLs."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        """Meta options for VideoSerializer."""

        model = Video
        fields = [
            "id",
            "title",
            "description",
            "category",
            "thumbnail_url",
            "created_at",
        ]

    def get_thumbnail_url(self, obj):
        """Return an absolute thumbnail URL if a generated thumbnail exists."""
        if not obj.thumbnail:
            return None

        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.thumbnail.url)

        backend_url = getattr(settings, "BACKEND_URL", "").rstrip("/")
        if backend_url:
            return f"{backend_url}{obj.thumbnail.url}"

        return None
