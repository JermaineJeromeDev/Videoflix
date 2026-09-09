import os
import posixpath
import subprocess
import tempfile

from django.conf import settings
from django.core.files import File
from django.core.files.storage import storages
from django_rq import job

from video_app.models import Video


def _download_video_to_temp(video_id, source_name):
    """Download a stored source video to a local path for FFmpeg."""
    if os.path.exists(source_name):
        return source_name, False

    source_path = os.path.join(
        tempfile.gettempdir(), "videoflix", f"source_{video_id}.mp4"
    )
    os.makedirs(os.path.dirname(source_path), exist_ok=True)
    storage = storages["default"]
    with storage.open(source_name, "rb") as source:
        with open(source_path, "wb") as destination:
            destination.write(source.read())
    return source_path, True


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
    """Return the storage name of the requested m3u8 file."""
    return posixpath.join("videos", str(movie_id), resolution, "index.m3u8")


def get_hls_segment_file(movie_id, resolution, segment):
    """Return the storage name of the requested ts segment."""
    return posixpath.join("videos", str(movie_id), resolution, segment)


@job
def extract_thumbnail_from_video(video_id, source_name):
    """Extract a single frame from the video at 1 second using FFMPEG as a thumbnail."""
    file_path, temporary = _download_video_to_temp(video_id, source_name)
    thumb_dir = os.path.join(tempfile.gettempdir(), "videoflix", "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)

    thumb_filename = f"thumb_{video_id}.jpg"
    thumb_path = os.path.join(thumb_dir, thumb_filename)

    timestamps = ["00:00:01", "00:00:00", "00:00:00.200"]
    generated = any(
        _run_thumbnail_capture(file_path, thumb_path, timestamp)
        for timestamp in timestamps
    )

    if generated:
        storage = storages["default"]
        storage_name = f"thumbnails/{thumb_filename}"
        with open(thumb_path, "rb") as thumbnail_file:
            storage.save(storage_name, File(thumbnail_file))
        Video.objects.filter(id=video_id).update(thumbnail=storage_name)
    else:

        Video.objects.filter(id=video_id).update(thumbnail=None)

    if temporary and os.path.exists(file_path):
        os.remove(file_path)


@job
def convert_to_hls_async(video_id, source_name, resolution, scale):
    """Execute the FFMPEG command as a background job to output HLS streams."""
    file_path, temporary = _download_video_to_temp(video_id, source_name)
    out_dir = os.path.join(
        tempfile.gettempdir(), "videoflix", "videos", str(video_id), resolution
    )
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
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    manifest_path = os.path.join(out_dir, "index.m3u8")
    if result.returncode != 0 or not os.path.exists(manifest_path):
        raise RuntimeError(f"FFmpeg failed to create {resolution} HLS output")

    storage = storages["default"]
    for filename in os.listdir(out_dir):
        output_path = os.path.join(out_dir, filename)
        storage_name = f"videos/{video_id}/{resolution}/{filename}"
        with open(output_path, "rb") as output_file:
            storage.save(storage_name, File(output_file))

    if temporary and os.path.exists(file_path):
        os.remove(file_path)
