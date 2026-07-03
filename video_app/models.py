from django.db import models


class Video(models.Model):
    """Video record supporting direct file uploads, thumbnails, and HLS generation."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    thumbnail = models.ImageField(upload_to="thumbnails/", blank=True, null=True)
    video_file = models.FileField(upload_to="videos_raw/", default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Video model."""

        ordering = ["-created_at", "-id"]

    def __str__(self):
        """Return the string representation of the video."""
        return self.title
