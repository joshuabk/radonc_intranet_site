from django.db import models


class ReportDefinition(models.Model):
    """A report that can be run from the reporting page.

    The framework ships with the registry and access control; the actual
    query execution against ARIA/MOSAIQ is implemented per-report in
    apps/reporting/queries/ once read-only DB credentials exist.
    """

    class Source(models.TextChoices):
        ARIA = "aria", "ARIA (Varian)"
        MOSAIQ = "mosaiq", "MOSAIQ (Elekta)"
        INTRANET = "intranet", "Intranet database"

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_DEV = "in_dev", "In development"
        LIVE = "live", "Live"
        DISABLED = "disabled", "Disabled"

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, help_text="Matches a query module in apps/reporting/queries/.")
    description = models.TextField(blank=True)
    source = models.CharField(max_length=10, choices=Source.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PLANNED)
    allowed_groups = models.ManyToManyField(
        "auth.Group", blank=True,
        help_text="Leave empty to allow everyone in the Reporting Access group.",
    )
    owner_notes = models.TextField(blank=True, help_text="SQL notes, table names, ticket links.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["source", "name"]

    def __str__(self):
        return self.name

    def user_can_run(self, user) -> bool:
        if user.is_superuser:
            return True
        groups = self.allowed_groups.all()
        if groups:
            return user.groups.filter(pk__in=groups).exists()
        from django.conf import settings
        return user.groups.filter(name=settings.SITE_GROUPS["REPORTING"]).exists()


class ReportRun(models.Model):
    """Audit trail: who ran what, when, and whether it succeeded."""
    report = models.ForeignKey(ReportDefinition, on_delete=models.CASCADE, related_name="runs")
    run_by = models.ForeignKey("auth.User", null=True, on_delete=models.SET_NULL)
    ran_at = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=False)
    row_count = models.IntegerField(null=True, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ["-ran_at"]

    def __str__(self):
        return f"{self.report} by {self.run_by} at {self.ran_at:%Y-%m-%d %H:%M}"
