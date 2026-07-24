from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from .models import NewStart, SpecialProcedure


def huddle_board(request):
    """Full-screen-friendly board for morning huddles."""
    today = timezone.localdate()
    week = today + timedelta(days=7)
    context = {
        "today": today,
        "starts_today": NewStart.objects.filter(start_date=today).select_related("location", "physicist"),
        "starts_week": (NewStart.objects.filter(start_date__gt=today, start_date__lte=week)
                        .select_related("location", "physicist")),
        "specials": (SpecialProcedure.objects
                     .filter(scheduled_for__date__gte=today, scheduled_for__date__lte=week)
                     .exclude(status=SpecialProcedure.Status.CANCELLED)
                     .select_related("procedure", "location", "physicist")),
    }
    return render(request, "huddle/board.html", context)
