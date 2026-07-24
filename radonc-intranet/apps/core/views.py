from datetime import date, timedelta

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from apps.contacts.models import ServiceContact
from apps.coverage.models import CoverageAssignment
from apps.huddle.models import NewStart, SpecialProcedure
from apps.linkhub.models import Link

from .models import Announcement


def home(request):
    now = timezone.now()
    today = timezone.localdate()
    announcements = Announcement.objects.filter(is_active=True).filter(
        Q(starts_at__isnull=True) | Q(starts_at__lte=now),
        Q(expires_at__isnull=True) | Q(expires_at__gte=now),
    )[:5]
    context = {
        "announcements": announcements,
        "quick_links": Link.objects.filter(is_active=True, pinned=True)[:8],
        "todays_coverage": (
            CoverageAssignment.objects.filter(start_date__lte=today, end_date__gte=today)
            .select_related("physicist", "location")
            .order_by("location__name")[:10]
        ),
        "upcoming_starts": (
            NewStart.objects.filter(start_date__gte=today, start_date__lte=today + timedelta(days=7))
            .select_related("location")
            .order_by("start_date")[:8]
        ),
        "upcoming_specials": (
            SpecialProcedure.objects.filter(scheduled_for__date__gte=today)
            .select_related("location")
            .order_by("scheduled_for")[:8]
        ),
    }
    return render(request, "core/home.html", context)


def search(request):
    """Lightweight cross-feature search (links and contacts for now)."""
    q = (request.GET.get("q") or "").strip()
    links = contacts = []
    if q:
        links = Link.objects.filter(is_active=True).filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(keywords__icontains=q)
        )[:25]
        contacts = ServiceContact.objects.filter(is_active=True).filter(
            Q(name__icontains=q) | Q(organization__icontains=q) | Q(systems__icontains=q)
        )[:25]
    return render(request, "core/search.html", {"q": q, "links": links, "contacts": contacts})
