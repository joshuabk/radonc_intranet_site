"""Root URL configuration. Each feature app owns its own urls.py."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.urls")),
    path("links/", include("apps.linkhub.urls")),
    path("contacts/", include("apps.contacts.urls")),
    path("coverage/", include("apps.coverage.urls")),
    path("huddle/", include("apps.huddle.urls")),
    path("reports/", include("apps.reporting.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
]
