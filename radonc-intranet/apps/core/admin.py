from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "pinned", "is_active", "created_at")
    list_filter = ("level", "is_active", "pinned")
    search_fields = ("title", "body")
