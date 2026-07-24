from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .datasources import source_is_configured
from .models import ReportDefinition


def _has_reporting_access(user):
    return user.is_superuser or user.groups.filter(
        name=settings.SITE_GROUPS["REPORTING"]).exists()


reporting_access_required = user_passes_test(_has_reporting_access, login_url="login")


@reporting_access_required
def report_list(request):
    reports = [r for r in ReportDefinition.objects.exclude(status="disabled")
               if r.user_can_run(request.user)]
    return render(request, "reporting/list.html", {
        "reports": reports,
        "aria_connected": source_is_configured("aria"),
        "mosaiq_connected": source_is_configured("mosaiq"),
    })


@reporting_access_required
def report_detail(request, slug):
    report = get_object_or_404(ReportDefinition, slug=slug)
    if not report.user_can_run(request.user):
        messages.error(request, "You don't have access to this report.")
        return redirect("reporting:list")
    # Framework stub: when a report goes live, its query module in
    # apps/reporting/queries/<slug>.py is invoked here and results rendered.
    return render(request, "reporting/detail.html", {
        "report": report,
        "source_connected": source_is_configured(report.source)
        or report.source == ReportDefinition.Source.INTRANET,
    })
