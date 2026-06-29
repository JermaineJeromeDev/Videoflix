from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model focusing on email login."""

    list_display = ("email", "is_active", "is_staff", "date_joined")
    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets
    add_fieldsets = UserAdmin.add_fieldsets


admin.site.register(CustomUser, CustomUserAdmin)
