from django.db import models


class ServiceContact(models.Model):
    """Service engineers and vendor support contacts (Varian, Elekta, IT...)."""

    class Kind(models.TextChoices):
        FIELD_ENGINEER = "engineer", "Field Service Engineer"
        VENDOR_SUPPORT = "vendor", "Vendor Support Line"
        INTERNAL = "internal", "Internal (Biomed / IT / Facilities)"
        OTHER = "other", "Other"

    name = models.CharField(max_length=150, help_text="Person or team name.")
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.FIELD_ENGINEER)
    organization = models.CharField(max_length=150, blank=True, help_text="Varian, Elekta, Sun Nuclear, hospital IT, ...")
    systems = models.CharField(max_length=255, blank=True,
                               help_text="Equipment / systems covered, e.g. TrueBeam 1-3, ARIA, HDR afterloader.")
    locations = models.ManyToManyField("coverage.Location", blank=True, related_name="service_contacts")
    phone = models.CharField(max_length=50, blank=True)
    after_hours_phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    support_portal_url = models.URLField(blank=True, help_text="e.g. Varian MyVarian / Elekta Care portal case link.")
    contract_notes = models.CharField(max_length=255, blank=True, help_text="Service contract / entitlement notes.")
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["organization", "name"]

    def __str__(self):
        return f"{self.name} ({self.organization})" if self.organization else self.name
