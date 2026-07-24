from django.contrib import admin

from .models import NewStart, SpecialProcedure


@admin.register(NewStart)
class NewStartAdmin(admin.ModelAdmin):
    list_display = ("mrn", "treatment_site", "technique", "location", "start_date", "status", "physicist")
    list_filter = ("status", "location", "technique")
    search_fields = ("mrn", "treatment_site")
    date_hierarchy = "start_date"
    list_editable = ("status",)


@admin.register(SpecialProcedure)
class SpecialProcedureAdmin(admin.ModelAdmin):
    list_display = ("procedure", "mrn", "location", "scheduled_for", "physicist", "status")
    list_filter = ("procedure", "location", "status")
    date_hierarchy = "scheduled_for"
    list_editable = ("status",)
