from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        # Core registers no feature card; it owns the home page itself.
        pass
