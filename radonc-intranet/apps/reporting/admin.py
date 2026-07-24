from django.contrib import admin

from .models import ReportDefinition, ReportRun


@admin.register(ReportDefinition)
class ReportDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "status", "updated_at")
    list_filter = ("source", "status")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("allowed_groups",)


@admin.register(ReportRun)
class ReportRunAdmin(admin.ModelAdmin):
    list_display = ("report", "run_by", "ran_at", "success", "row_count")
    list_filter = ("success", "report")
    readonly_fields = ("report", "run_by", "ran_at", "parameters", "success", "row_count", "error")
