from django.apps import AppConfig


class CoverageConfig(AppConfig):
    name = "apps.coverage"
    verbose_name = "Coverage"

    def ready(self):
        from apps.core.registry import Feature, NavItem, registry

        registry.register(Feature(
            slug="coverage",
            title="Coverage",
            description="Today's physics coverage, upcoming assignments, the coverage matrix, and PTO calendars.",
            url_name="coverage:home",
            icon="calendar",
            order=30,
            hidden=True,  # not functional yet; remove to show in nav/home
            section="Operations",
            nav_items=[NavItem("Coverage matrix", "coverage:matrix")],
        ))
