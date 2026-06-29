import os
import subprocess

from django.conf import settings
from django_rq import job


def get_hls_manifest_file(movie_id, resolution):
    """Return the absolute path of the m3u8 file if it exists, otherwise None."""
    relative_path = os.path.join("videos", str(movie_id), resolution, "index.m3u8")
    absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    if os.path.exists(absolute_path):
        return absolute_path
    return None


def get_hls_segment_file(movie_id, resolution, segment):
    """Return the absolute path of the ts segment if it exists, otherwise None."""
    relative_path = os.path.join("videos", str(movie_id), resolution, segment)
    absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    if os.path.exists(absolute_path):
        return absolute_path
    return None


@job
def convert_to_hls_async(video_id, file_path, resolution, scale):
    """Execute the FFMPEG command as a background job to output HLS streams."""
    out_dir = os.path.join(settings.MEDIA_ROOT, "videos", str(video_id), resolution)
    os.makedirs(out_dir, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-i",
        file_path,
        "-vf",
        f"scale={scale}",
        "-start_number",
        "0",
        "-hls_time",
        "10",
        "-hls_list_size",
        "0",
        "-f",
        "hls",
        os.path.join(out_dir, "index.m3u8"),
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
