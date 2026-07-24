"""Create the named permission groups the site relies on.

Run once after the first migrate:  python manage.py bootstrap_site
Safe to re-run (idempotent).
"""
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the standard authorization groups (Physics, Reporting Access, ...)."

    def handle(self, *args, **options):
        for key, name in settings.SITE_GROUPS.items():
            group, created = Group.objects.get_or_create(name=name)
            verb = "Created" if created else "Exists"
            self.stdout.write(f"  {verb}: {name}")
        self.stdout.write(self.style.SUCCESS("Groups ready."))
