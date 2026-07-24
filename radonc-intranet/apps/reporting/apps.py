from django.apps import AppConfig
from django.conf import settings


class ReportingConfig(AppConfig):
    name = "apps.reporting"
    verbose_name = "Reporting"

    def ready(self):
        from apps.core.registry import Feature, registry

        registry.register(Feature(
            slug="reporting",
            title="Reports",
            description="Run approved reports against ARIA and MOSAIQ. Access limited to the Reporting group.",
            url_name="reporting:list",
            icon="report",
            order=50,
            section="Operations",
            required_group=settings.SITE_GROUPS["REPORTING"],
        ))
