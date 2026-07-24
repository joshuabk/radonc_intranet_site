from django.contrib import admin

from .models import (Capability, CoverageAssignment, ExternalCalendar,
                     Location, Physicist, ProcedureType)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "short_code", "machines", "is_active", "order")
    list_editable = ("order", "is_active")


@admin.register(ProcedureType)
class ProcedureTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation", "requires_credentialing", "is_active", "order")
    list_editable = ("order", "is_active")


class CapabilityInline(admin.TabularInline):
    model = Capability
    extra = 0
    filter_horizontal = ("locations",)


@admin.register(Physicist)
class PhysicistAdmin(admin.ModelAdmin):
    list_display = ("display_name", "initials", "role", "primary_location", "phone", "is_active")
    list_filter = ("role", "primary_location", "is_active")
    search_fields = ("display_name", "initials", "email")
    inlines = [CapabilityInline]


@admin.register(Capability)
class CapabilityAdmin(admin.ModelAdmin):
    list_display = ("physicist", "procedure", "level", "credentialed_on", "expires_on")
    list_filter = ("level", "procedure", "locations")
    filter_horizontal = ("locations",)


@admin.register(CoverageAssignment)
class CoverageAssignmentAdmin(admin.ModelAdmin):
    list_display = ("physicist", "duty", "location", "start_date", "end_date")
    list_filter = ("duty", "location")
    date_hierarchy = "start_date"


@admin.register(ExternalCalendar)
class ExternalCalendarAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "url", "embed", "is_active", "order")
    list_editable = ("order", "is_active")
