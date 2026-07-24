from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from .models import (Capability, CoverageAssignment, ExternalCalendar,
                     Location, Physicist, ProcedureType)


def coverage_home(request):
    """Current assignments, the next two weeks, and PTO calendar links."""
    today = timezone.localdate()
    horizon = today + timedelta(days=14)
    current = (
        CoverageAssignment.objects.filter(start_date__lte=today, end_date__gte=today)
        .select_related("physicist", "location")
    )
    upcoming = (
        CoverageAssignment.objects.filter(start_date__gt=today, start_date__lte=horizon)
        .select_related("physicist", "location")
    )
    calendars = ExternalCalendar.objects.filter(is_active=True)
    return render(request, "coverage/home.html", {
        "today": today,
        "current": current,
        "upcoming": upcoming,
        "calendars": calendars,
    })


def coverage_matrix(request):
    """Physicist × procedure grid, filterable by location."""
    locations = Location.objects.filter(is_active=True)
    procedures = ProcedureType.objects.filter(is_active=True)
    physicists = Physicist.objects.filter(is_active=True).select_related("primary_location")

    loc_id = request.GET.get("location") or ""
    caps = Capability.objects.select_related("physicist", "procedure").prefetch_related("locations")
    if loc_id.isdigit():
        # A capability applies at a location if it lists it OR lists none (= all).
        caps = [c for c in caps if not c.locations.exists()
                or c.locations.filter(pk=int(loc_id)).exists()]

    cap_lookup = {(c.physicist_id, c.procedure_id): c for c in caps}
    rows = []
    for p in physicists:
        cells = [cap_lookup.get((p.id, proc.id)) for proc in procedures]
        rows.append({"physicist": p, "cells": cells})

    return render(request, "coverage/matrix.html", {
        "locations": locations,
        "procedures": procedures,
        "rows": rows,
        "selected_location": int(loc_id) if loc_id.isdigit() else None,
    })
