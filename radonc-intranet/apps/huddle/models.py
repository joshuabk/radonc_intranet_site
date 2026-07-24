"""
Huddle board: the daily physics/department huddle dashboard.

PHI note: these tables are designed to hold the minimum necessary
identifiers (MRN + initials, not full names). Access is already limited to
authenticated staff; review with your privacy office before go-live.
"""
from django.db import models

from apps.coverage.models import Location, Physicist, ProcedureType


class NewStart(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Plan in progress"
        READY = "ready", "Ready for treatment"
        STARTED = "started", "Started"
        HELD = "held", "On hold"

    mrn = models.CharField("MRN", max_length=20, help_text="Medical record number (minimum necessary identifier).")
    patient_initials = models.CharField(max_length=8, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    machine = models.CharField(max_length=60, blank=True)
    treatment_site = models.CharField(max_length=120, help_text="e.g. Left breast, Prostate, Brain mets.")
    technique = models.CharField(max_length=60, blank=True, help_text="e.g. VMAT, 3D, SBRT, DIBH.")
    fractions = models.CharField(max_length=30, blank=True, help_text="e.g. 28 fx, 5 fx.")
    start_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    physicist = models.ForeignKey(Physicist, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_date", "location__order"]

    def __str__(self):
        return f"{self.mrn} — {self.treatment_site} ({self.start_date})"


class SpecialProcedure(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PREP = "in_prep", "In preparation"
        DONE = "done", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    procedure = models.ForeignKey(ProcedureType, on_delete=models.PROTECT)
    mrn = models.CharField("MRN", max_length=20, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    scheduled_for = models.DateTimeField()
    physicist = models.ForeignKey(Physicist, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="special_procedures")
    backup_physicist = models.ForeignKey(Physicist, null=True, blank=True, on_delete=models.SET_NULL,
                                         related_name="special_procedures_backup")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_for"]

    def __str__(self):
        return f"{self.procedure} @ {self.location} ({self.scheduled_for:%Y-%m-%d %H:%M})"
