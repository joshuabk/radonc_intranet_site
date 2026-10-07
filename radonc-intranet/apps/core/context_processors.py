from django.conf import settings

from .registry import registry


def site_context(request):
    features = registry.for_user(request.user)
    return {
        "SITE_NAME": settings.SITE_NAME,
        "ORG_NAME": settings.ORG_NAME,
        "nav_sections": registry.sections_for_user(request.user),
        "features": features,
        "feature_slugs": [f.slug for f in features],
    }
