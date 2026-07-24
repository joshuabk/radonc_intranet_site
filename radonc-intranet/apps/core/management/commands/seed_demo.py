"""Load realistic example data so the framework can be demoed immediately.

    python manage.py seed_demo

Idempotent: uses get_or_create throughout. All data is fictional.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.contacts.models import ServiceContact
from apps.core.models import Announcement
from apps.coverage.models import (Capability, CoverageAssignment,
                                  ExternalCalendar, Location, Physicist,
                                  ProcedureType)
from apps.huddle.models import NewStart, SpecialProcedure
from apps.linkhub.models import Link, LinkCategory
from apps.reporting.models import ReportDefinition


class Command(BaseCommand):
    help = "Load fictional demo data for every feature."

    def handle(self, *args, **options):
        today = timezone.localdate()
        now = timezone.now()

        # ---- Locations -----------------------------------------------
        main, _ = Location.objects.get_or_create(
            short_code="MAIN", defaults=dict(name="Main Campus", order=10,
            machines="TrueBeam 1-2, Ethos, HDR suite, CT sim"))
        north, _ = Location.objects.get_or_create(
            short_code="NORTH", defaults=dict(name="North Cancer Center", order=20,
            machines="TrueBeam 3, CT sim"))
        east, _ = Location.objects.get_or_create(
            short_code="EAST", defaults=dict(name="East Satellite Clinic", order=30,
            machines="VitalBeam 1"))

        # ---- Link hub -------------------------------------------------
        cats = {}
        for name, order, desc in [
            ("Clinical Systems", 10, "Treatment management & planning"),
            ("Documents & Policies", 20, "Policies, procedures, forms"),
            ("File Shares", 30, "Network drives"),
            ("Reports & Dashboards", 40, ""),
        ]:
            cats[name], _ = LinkCategory.objects.get_or_create(name=name, defaults=dict(order=order, description=desc))

        links = [
            ("Clinical Systems", "ARIA (Varian)", "https://aria.hospital.internal", "Record & verify, scheduling, charting", "beam", True),
            ("Clinical Systems", "MOSAIQ (Elekta)", "https://mosaiq.hospital.internal", "Record & verify for Elekta sites", "beam", True),
            ("Clinical Systems", "Citrix Workspace", "https://citrix.hospital.internal", "Eclipse, RayStation, and other published apps", "citrix", True),
            ("Documents & Policies", "LucidDoc — Policies & Procedures", "https://luciddoc.hospital.internal", "Controlled department policies and procedures", "document", True),
            ("Documents & Policies", "SharePoint — Radiation Oncology", "https://sharepoint.hospital.internal/sites/radonc", "Department site: meeting minutes, schedules, forms", "document", False),
            ("Documents & Policies", "Forms Library", "https://sharepoint.hospital.internal/sites/radonc/forms", "Printable and electronic department forms", "form", False),
            ("File Shares", "P: Drive — Physics", r"\\fileserver\physics", "QA data, commissioning, annual reports", "folder", False),
            ("File Shares", "P: Drive — Dosimetry", r"\\fileserver\dosimetry", "Planning resources and templates", "folder", False),
            ("Reports & Dashboards", "Monthly QA Report Portal", "https://reports.hospital.internal/qa", "Machine QA summaries", "report", False),
        ]
        for cat, title, url, desc, icon, pinned in links:
            Link.objects.get_or_create(title=title, defaults=dict(
                category=cats[cat], url=url, description=desc, icon=icon, pinned=pinned))

        # ---- Physics staff & matrix ----------------------------------
        staff = [
            ("Sarah Chen, PhD", "SC", main), ("Marcus Webb, MS", "MW", main),
            ("Priya Raman, PhD", "PR", north), ("David Okafor, MS", "DO", east),
            ("Lena Fischer, MS", "LF", main),
        ]
        people = {}
        for name, initials, loc in staff:
            people[initials], _ = Physicist.objects.get_or_create(
                initials=initials, defaults=dict(display_name=name, primary_location=loc,
                                                 phone=f"x5{ord(initials[0])}{ord(initials[1])}"))

        procs = {}
        for name, abbr, order, cred in [
            ("Stereotactic Radiosurgery", "SRS", 10, True),
            ("Stereotactic Body RT", "SBRT", 20, True),
            ("HDR Brachytherapy", "HDR", 30, True),
            ("Total Body Irradiation", "TBI", 40, True),
            ("Respiratory Gating / DIBH", "Gating", 50, False),
            ("Ethos Adaptive", "Adaptive", 60, True),
        ]:
            procs[abbr], _ = ProcedureType.objects.get_or_create(
                name=name, defaults=dict(abbreviation=abbr, order=order, requires_credentialing=cred))

        matrix = [
            ("SC", "SRS", "primary"), ("SC", "SBRT", "primary"), ("SC", "Adaptive", "primary"),
            ("SC", "Gating", "primary"),
            ("MW", "SBRT", "primary"), ("MW", "HDR", "primary"), ("MW", "TBI", "backup"),
            ("MW", "Gating", "primary"),
            ("PR", "SRS", "backup"), ("PR", "SBRT", "primary"), ("PR", "TBI", "primary"),
            ("PR", "Gating", "primary"),
            ("DO", "SBRT", "backup"), ("DO", "Gating", "primary"), ("DO", "HDR", "training"),
            ("LF", "HDR", "primary"), ("LF", "Adaptive", "training"), ("LF", "SBRT", "training"),
        ]
        for who, what, level in matrix:
            Capability.objects.get_or_create(
                physicist=people[who], procedure=procs[what], defaults=dict(level=level))

        # ---- Coverage assignments & calendars ------------------------
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=4)
        assignments = [
            ("SC", main, "clinical"), ("MW", main, "hdr"),
            ("PR", north, "clinical"), ("DO", east, "clinical"),
            ("LF", None, "on_call"),
        ]
        for who, loc, duty in assignments:
            CoverageAssignment.objects.get_or_create(
                physicist=people[who], location=loc, duty=duty,
                start_date=week_start, end_date=week_end)
        CoverageAssignment.objects.get_or_create(
            physicist=people["MW"], location=north, duty="clinical",
            start_date=week_start + timedelta(days=7), end_date=week_end + timedelta(days=7),
            defaults=dict(notes="Covering for PR (PTO)"))

        for name, kind, url in [
            ("Physics PTO Calendar (Outlook)", "pto", "https://outlook.hospital.internal/owa/calendar/physics-pto"),
            ("Physics On-Call (QGenda)", "on_call", "https://app.qgenda.com/link/physics-oncall"),
            ("Dosimetry PTO Calendar", "pto", "https://outlook.hospital.internal/owa/calendar/dosimetry-pto"),
        ]:
            ExternalCalendar.objects.get_or_create(name=name, defaults=dict(kind=kind, url=url))

        # ---- Huddle board ---------------------------------------------
        starts = [
            ("10238471", "Left breast", "DIBH", main, "TrueBeam 1", 0, "ready", "SC", "16 fx"),
            ("10245890", "Prostate", "VMAT", north, "TrueBeam 3", 0, "started", "PR", "28 fx"),
            ("10250013", "Brain mets x3", "SRS", main, "TrueBeam 2", 1, "pending", "SC", "1 fx"),
            ("10251777", "Lung RUL", "SBRT", main, "TrueBeam 2", 2, "pending", "MW", "5 fx"),
            ("10252104", "Rectum", "VMAT", east, "VitalBeam 1", 3, "ready", "DO", "25 fx"),
            ("10253335", "H&N", "VMAT", main, "Ethos", 5, "held", "SC", "33 fx"),
        ]
        for mrn, site, tech, loc, machine, offset, status, who, fx in starts:
            NewStart.objects.get_or_create(mrn=mrn, defaults=dict(
                treatment_site=site, technique=tech, location=loc, machine=machine,
                start_date=today + timedelta(days=offset), status=status,
                physicist=people[who], fractions=fx))

        specials = [
            ("HDR", "10247212", main, 1, 9, "MW", "LF", "scheduled", "Cervix, fraction 2 of 5"),
            ("SRS", "10250013", main, 1, 13, "SC", "PR", "in_prep", "Frame-based, 3 targets"),
            ("TBI", "10249406", main, 3, 7, "PR", "MW", "scheduled", "AM session, 12 Gy / 6 fx BID"),
        ]
        for abbr, mrn, loc, d_off, hour, who, backup, status, notes in specials:
            when = (now + timedelta(days=d_off)).replace(hour=hour, minute=0, second=0, microsecond=0)
            SpecialProcedure.objects.get_or_create(
                procedure=procs[abbr], mrn=mrn, location=loc, scheduled_for=when,
                defaults=dict(physicist=people[who], backup_physicist=people[backup],
                              status=status, notes=notes))

        # ---- Service contacts -----------------------------------------
        contacts = [
            ("Tom Delgado", "engineer", "Varian", "TrueBeam 1-3, Ethos", "555-0142", "800-555-7300", "tom.delgado@example.com"),
            ("Varian Helpdesk (ARIA/Eclipse)", "vendor", "Varian", "ARIA, Eclipse, Ethos software", "888-555-8200", "888-555-8200", ""),
            ("Elekta Care Support", "vendor", "Elekta", "MOSAIQ, VitalBeam", "888-555-3500", "888-555-3500", ""),
            ("Biomedical Engineering", "internal", "Hospital", "CT sims, lasers, monitors", "x4471", "x4471", ""),
            ("Radiation Oncology IT", "internal", "Hospital IT", "Citrix, SharePoint, network shares", "x2200", "x2200", "radonc-it@example.com"),
        ]
        for name, kind, org, systems, phone, after, email in contacts:
            c, _ = ServiceContact.objects.get_or_create(name=name, defaults=dict(
                kind=kind, organization=org, systems=systems,
                phone=phone, after_hours_phone=after, email=email))
            if not c.locations.exists():
                c.locations.set([main, north, east])

        # ---- Reports (framework registry) -----------------------------
        for name, slug, source, status, desc in [
            ("New starts last 30 days", "aria-new-starts", "aria", "planned",
             "Patients with first treatment in the last 30 days, by site and technique."),
            ("Weekly chart check worklist", "mosaiq-chart-checks", "mosaiq", "planned",
             "Patients due for weekly physics chart check at MOSAIQ sites."),
            ("Special procedures volume", "intranet-specials-volume", "intranet", "in_dev",
             "Counts of SRS/SBRT/HDR/TBI cases by month from the huddle board."),
        ]:
            ReportDefinition.objects.get_or_create(slug=slug, defaults=dict(
                name=name, source=source, status=status, description=desc))

        # ---- Announcement ---------------------------------------------
        Announcement.objects.get_or_create(
            title="Welcome to the new Radiation Oncology intranet",
            defaults=dict(level="info", pinned=True,
                          body="Link hub, coverage, contacts, and the huddle board are live. "
                               "Send feedback to the physics office."))
        Announcement.objects.get_or_create(
            title="TrueBeam 2 PM scheduled Thursday 06:00–08:00",
            defaults=dict(level="notice",
                          body="Varian FSE on site. First patient at 08:30."))

        self.stdout.write(self.style.SUCCESS("Demo data loaded (all fictional)."))
