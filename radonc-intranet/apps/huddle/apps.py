from django.apps import AppConfig


class HuddleConfig(AppConfig):
    name = "apps.huddle"
    verbose_name = "Huddle Board"

    def ready(self):
        from apps.core.registry import Feature, registry

        registry.register(Feature(
            slug="huddle",
            title="Huddle Board",
            description="New starts and special procedures for daily physics and department huddles.",
            url_name="huddle:board",
            icon="monitor",
            order=40,
            section="Operations",
        ))
