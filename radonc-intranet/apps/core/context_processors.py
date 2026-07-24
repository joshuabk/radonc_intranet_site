from django.conf import settings

from .registry import registry


def site_context(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "ORG_NAME": settings.ORG_NAME,
        "nav_sections": registry.sections_for_user(request.user),
        "features": registry.for_user(request.user),
    }
