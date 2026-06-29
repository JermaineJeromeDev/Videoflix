from django.db.models.signals import post_save
from django.dispatch import receiver

from .api.utils import convert_to_hls_async
from .models import Video


@receiver(post_save, sender=Video)
def queue_video_conversion(sender, instance, created, **kwargs):
    """Trigger background HLS processing when a new video file is provided."""
    if created and instance.video_file:
        raw_path = instance.video_file.path
        convert_to_hls_async.delay(instance.id, raw_path, "480p", "854:480")
        convert_to_hls_async.delay(instance.id, raw_path, "720p", "1280:720")
        convert_to_hls_async.delay(instance.id, raw_path, "1080p", "1920:1080")
