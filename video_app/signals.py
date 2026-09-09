import os
import shutil
import tempfile

from django.conf import settings
from django.core.files.storage import storages
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .api.utils import convert_to_hls_async, extract_thumbnail_from_video
from .models import Video


@receiver(post_save, sender=Video)
def queue_video_conversion(sender, instance, created, **kwargs):
    """Trigger background HLS processing and thumbnail extraction when a video is added."""
    if created and instance.video_file:
        source_name = instance.video_file.name

        extract_thumbnail_from_video.delay(instance.id, source_name)

        convert_to_hls_async.delay(instance.id, source_name, "480p", "854:480")
        convert_to_hls_async.delay(instance.id, source_name, "720p", "1280:720")
        convert_to_hls_async.delay(instance.id, source_name, "1080p", "1920:1080")


@receiver(post_delete, sender=Video)
def delete_video_files_from_disk(sender, instance, **kwargs):
    """Delete all associated HLS chunks, raw videos, and thumbnails."""
    storage = storages["default"]
    if instance.video_file:
        storage.delete(instance.video_file.name)

    if instance.thumbnail:
        storage.delete(instance.thumbnail.name)

    hls_folder = os.path.join(
        getattr(settings, "MEDIA_ROOT", tempfile.gettempdir()),
        "videos",
        str(instance.id),
    )
    if os.path.exists(hls_folder):
        shutil.rmtree(hls_folder)
