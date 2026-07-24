from django.apps import AppConfig


class ContactsConfig(AppConfig):
    name = "apps.contacts"
    verbose_name = "Service Contacts"

    def ready(self):
        from apps.core.registry import Feature, registry

        registry.register(Feature(
            slug="contacts",
            title="Service Contacts",
            description="Field service engineers, vendor support lines, and after-hours numbers by machine and site.",
            url_name="contacts:list",
            icon="phone",
            order=20,
            section="Workspace",
        ))
