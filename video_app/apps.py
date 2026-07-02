from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    """Configuration for the video_app application catalog."""

    name = "video_app"

    """Override the ready method to import signals when the app is ready."""

    def ready(self):
        from . import signals  # noqa: F401
