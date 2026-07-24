from django.db import models


class LinkCategory(models.Model):
    """Groups on the link hub page: Clinical Systems, Documents, IT, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Link categories"

    def __str__(self):
        return self.name


class Link(models.Model):
    """A single destination: ARIA, MOSAIQ, Citrix, SharePoint, P: drive,
    LucidDoc policies, forms, report portals, and anything added later."""

    category = models.ForeignKey(LinkCategory, on_delete=models.PROTECT, related_name="links")
    title = models.CharField(max_length=150)
    url = models.CharField(
        max_length=500,
        help_text="http(s) URL, or a UNC/file path like \\\\fileserver\\physics (shown with a copy button).",
    )
    description = models.CharField(max_length=255, blank=True)
    keywords = models.CharField(max_length=255, blank=True, help_text="Extra search terms, comma separated.")
    icon = models.CharField(max_length=40, blank=True, default="link",
                            help_text="Icon key from the built-in set (link, beam, database, document, citrix, folder, report, form).")
    pinned = models.BooleanField(default=False, help_text="Pinned links appear in Quick Links on the home page.")
    open_in_new_tab = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=100)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category__order", "order", "title"]

    def __str__(self):
        return self.title

    @property
    def is_unc_path(self) -> bool:
        return self.url.startswith("\\\\") or self.url.lower().startswith("file:")
