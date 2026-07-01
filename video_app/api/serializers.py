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
        """Return the absolute URL of the thumbnail image if it exists."""
        request = self.context.get("request")
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None
