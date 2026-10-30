from django.conf import settings
from django.http import FileResponse


def robots_txt(request):
    return FileResponse(
        (settings.BASE_DIR / "robots.txt").open("rb"),
        content_type="text/plain",
    )
