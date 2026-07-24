from django.contrib import admin

from .models import Link, LinkCategory


class LinkInline(admin.TabularInline):
    model = Link
    extra = 0
    fields = ("title", "url", "icon", "pinned", "is_active", "order")


@admin.register(LinkCategory)
class LinkCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    inlines = [LinkInline]


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "pinned", "is_active", "order", "updated_at")
    list_filter = ("category", "pinned", "is_active")
    search_fields = ("title", "description", "keywords", "url")
    list_editable = ("pinned", "is_active", "order")
