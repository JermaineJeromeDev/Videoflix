import os
import subprocess

from django.conf import settings
from django_rq import job

from video_app.models import Video


def _run_thumbnail_capture(file_path, thumb_path, timestamp):
    """Run ffmpeg for a single timestamp and report whether a file was produced."""
    cmd = [
        "ffmpeg",
        "-ss",
        timestamp,
        "-i",
        file_path,
        "-vframes",
        "1",
        "-q:v",
        "2",
        thumb_path,
        "-y",
    ]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0 and os.path.exists(thumb_path)


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
def extract_thumbnail_from_video(video_id, file_path):
    """Extract a single frame from the video at 1 second using FFMPEG as a thumbnail."""
    thumb_dir = os.path.join(settings.MEDIA_ROOT, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)

    thumb_filename = f"thumb_{video_id}.jpg"
    thumb_path = os.path.join(thumb_dir, thumb_filename)

    timestamps = ["00:00:01", "00:00:00", "00:00:00.200"]
    generated = any(
        _run_thumbnail_capture(file_path, thumb_path, timestamp)
        for timestamp in timestamps
    )

    if generated:
        Video.objects.filter(id=video_id).update(
            thumbnail=f"thumbnails/{thumb_filename}"
        )
    else:

        Video.objects.filter(id=video_id).update(thumbnail=None)


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
