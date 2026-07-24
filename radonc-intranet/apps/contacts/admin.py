from django.contrib import admin

from .models import ServiceContact


@admin.register(ServiceContact)
class ServiceContactAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "kind", "systems", "phone", "is_active")
    list_filter = ("kind", "organization", "is_active", "locations")
    search_fields = ("name", "organization", "systems", "notes")
    filter_horizontal = ("locations",)
