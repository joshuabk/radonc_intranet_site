from django.conf import settings
from django.db import models


class Announcement(models.Model):
    """Department-wide announcements shown on the home page."""

    class Level(models.TextChoices):
        INFO = "info", "Info"
        NOTICE = "notice", "Notice"
        URGENT = "urgent", "Urgent"

    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.INFO)
    is_active = models.BooleanField(default=True)
    pinned = models.BooleanField(default=False, help_text="Pinned announcements stay at the top.")
    starts_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-pinned", "-created_at"]

    def __str__(self):
        return self.title
