from rest_framework import serializers

from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializer to map the Video model instance into JSON format."""

    class Meta:
        """Meta options for VideoSerializer."""

        model = Video
        fields = ["id", "title", "description", "category", "created_at"]
