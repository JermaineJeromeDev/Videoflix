import os

from django.conf import settings


def get_hls_manifest_file(movie_id, resolution):
    """Return the absolute path of the m3u8 file if it exists, otherwise None."""
    relative_path = os.path.join("videos", str(movie_id), resolution, "index.m3u8")
    absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    if os.path.exists(absolute_path):
        return absolute_path
    return None
