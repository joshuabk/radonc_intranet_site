from django.conf import settings
from django.db import models


class Location(models.Model):
    """A treatment site / campus in the hospital system."""
    name = models.CharField(max_length=120, unique=True)
    short_code = models.CharField(max_length=12, unique=True, help_text="Badge shown in tables, e.g. MAIN, NORTH.")
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    machines = models.CharField(max_length=255, blank=True, help_text="e.g. TrueBeam x2, Ethos, HDR suite.")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class ProcedureType(models.Model):
    """A procedure/competency that requires physics coverage: SRS, SBRT,
    HDR, TBI, gating, prostate seeds, Gamma Knife, etc."""
    name = models.CharField(max_length=120, unique=True)
    abbreviation = models.CharField(max_length=20, blank=True)
    description = models.CharField(max_length=255, blank=True)
    requires_credentialing = models.BooleanField(
        default=False, help_text="Procedure requires documented competency/credentialing."
    )
    order = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.abbreviation or self.name


class Physicist(models.Model):
    """A physics staff member. Optionally linked to a login account."""

    class Role(models.TextChoices):
        PHYSICIST = "physicist", "Medical Physicist"
        RESIDENT = "resident", "Physics Resident"
        ASSISTANT = "assistant", "Physics Assistant"
        DOSIMETRIST = "dosimetrist", "Dosimetrist"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Link to a site login so this person sees their own assignments.",
    )
    display_name = models.CharField(max_length=120)
    initials = models.CharField(max_length=8, help_text="Shown in the coverage matrix and calendars.")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PHYSICIST)
    primary_location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=50, blank=True)
    pager = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_name"]
        verbose_name = "Physics staff member"
        verbose_name_plural = "Physics staff"

    def __str__(self):
        return self.display_name


class Capability(models.Model):
    """One cell of the coverage matrix: which physicist can cover which
    procedure, and at which locations."""

    class Level(models.TextChoices):
        PRIMARY = "primary", "Primary (independent)"
        BACKUP = "backup", "Backup (can cover)"
        TRAINING = "training", "In training"

    physicist = models.ForeignKey(Physicist, on_delete=models.CASCADE, related_name="capabilities")
    procedure = models.ForeignKey(ProcedureType, on_delete=models.CASCADE, related_name="capabilities")
    locations = models.ManyToManyField(
        Location, blank=True,
        help_text="Leave empty to mean 'all locations'.",
    )
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.PRIMARY)
    credentialed_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True, help_text="If competency must be renewed.")
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = [("physicist", "procedure")]
        verbose_name_plural = "Capabilities"

    def __str__(self):
        return f"{self.physicist} — {self.procedure} ({self.get_level_display()})"


class CoverageAssignment(models.Model):
    """Who is covering a location (or duty) for a date range."""

    class Duty(models.TextChoices):
        CLINICAL = "clinical", "Clinical coverage"
        ON_CALL = "on_call", "On call"
        HDR = "hdr", "HDR coverage"
        SPECIALS = "specials", "Special procedures"
        REMOTE = "remote", "Remote / planning"

    physicist = models.ForeignKey(Physicist, on_delete=models.CASCADE, related_name="assignments")
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL,
                                 help_text="Blank for system-wide duties like on call.")
    duty = models.CharField(max_length=20, choices=Duty.choices, default=Duty.CLINICAL)
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date", "location__order"]

    def __str__(self):
        where = self.location or "All sites"
        return f"{self.physicist} @ {where} ({self.start_date}–{self.end_date})"


class ExternalCalendar(models.Model):
    """Links out to PTO / on-call calendars that live elsewhere
    (Outlook shared calendar, QGenda, Amion, SharePoint list, ...)."""

    class Kind(models.TextChoices):
        PTO = "pto", "PTO calendar"
        ON_CALL = "on_call", "On-call schedule"
        ROTATION = "rotation", "Rotation schedule"
        OTHER = "other", "Other"

    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.PTO)
    url = models.CharField(max_length=500)
    description = models.CharField(max_length=255, blank=True)
    embed = models.BooleanField(
        default=False,
        help_text="If the calendar supports iframe embedding on the intranet, show it inline.",
    )
    order = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name
