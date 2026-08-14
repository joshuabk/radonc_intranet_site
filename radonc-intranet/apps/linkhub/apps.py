from django.apps import AppConfig


class LinkhubConfig(AppConfig):
    name = "apps.linkhub"
    verbose_name = "Link Hub"

    def ready(self):
        from apps.core.registry import Feature, registry

        registry.register(Feature(
            slug="linkhub",
            title="Link Hub",
            description="Application and document links",
            url_name="linkhub:hub",
            icon="link",
            order=10,
            section="Workspace",
            # The Link Hub is open to everyone -- it stays visible in the nav
            # and reachable even when REQUIRE_LOGIN is switched on. Its view
            # is marked @login_not_required to match (see views.py).
            public=True,
        ))
