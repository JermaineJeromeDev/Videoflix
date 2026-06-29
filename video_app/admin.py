from django.contrib import admin

from .models import Video


class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for the Video catalog interface."""

    list_display = ("title", "category", "created_at")
    search_fields = ("title", "category")


admin.site.register(Video, VideoAdmin)
