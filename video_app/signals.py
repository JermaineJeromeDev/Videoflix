import os
import shutil

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .api.utils import convert_to_hls_async, extract_thumbnail_from_video
from .models import Video


@receiver(post_save, sender=Video)
def queue_video_conversion(sender, instance, created, **kwargs):
    """Trigger background HLS processing and thumbnail extraction when a video is added."""
    if created and instance.video_file:
        raw_path = instance.video_file.path

        extract_thumbnail_from_video.delay(instance.id, raw_path)

        convert_to_hls_async.delay(instance.id, raw_path, "480p", "854:480")
        convert_to_hls_async.delay(instance.id, raw_path, "720p", "1280:720")
        convert_to_hls_async.delay(instance.id, raw_path, "1080p", "1920:1080")


@receiver(post_delete, sender=Video)
def delete_video_files_from_disk(sender, instance, **kwargs):
    """Delete all associated HLS chunks, raw videos, and thumbnails from disk."""
    if instance.video_file and os.path.exists(instance.video_file.path):
        os.remove(instance.video_file.path)

    if instance.thumbnail and os.path.exists(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)

    hls_folder = os.path.join(settings.MEDIA_ROOT, "videos", str(instance.id))
    if os.path.exists(hls_folder):
        shutil.rmtree(hls_folder)
