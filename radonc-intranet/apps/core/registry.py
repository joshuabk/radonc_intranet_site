"""
Feature registry: the extension point for adding large features to the site.

Each feature app declares itself in its AppConfig.ready() by calling
registry.register(...). The base template then renders the sidebar
navigation, and the home page renders one card per feature, automatically.

Adding a new major feature later (e.g. an equipment QA tracker) is:

    1. python manage.py startapp qa apps/qa
    2. Add "apps.qa" to LOCAL_APPS in config/settings/base.py
    3. Add its urls.py to config/urls.py
    4. In apps/qa/apps.py ready(), call registry.register(Feature(...))

No template or navigation edits required.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NavItem:
    """A secondary link shown under a feature in the sidebar."""
    label: str
    url_name: str  # named URL, reversed in the template


@dataclass
class Feature:
    slug: str                  # unique key, e.g. "coverage"
    title: str                 # sidebar / card title
    description: str           # one-liner shown on the home page card
    url_name: str              # named URL of the feature's landing page
    icon: str = "grid"         # key into the inline SVG icon set (icons.html)
    order: int = 100           # sidebar position (lower = higher)
    section: str = "Workspace" # sidebar grouping header
    required_group: str | None = None   # group name; None = all signed-in staff
    staff_only: bool = False
    public: bool = False       # visible to signed-out visitors even when
                               # REQUIRE_LOGIN is on; the feature's own views
                               # must also be marked @login_not_required
    nav_items: list[NavItem] = field(default_factory=list)

    def visible_to(self, user) -> bool:
        if not user.is_authenticated:
            # A gated feature is never shown to signed-out visitors.
            if self.staff_only or self.required_group:
                return False
            # public=True features are always shown (e.g. the Link Hub).
            if self.public:
                return True
            # Otherwise they are shown only while the site-wide login
            # requirement is switched off (REQUIRE_LOGIN = False).
            from django.conf import settings

            return not getattr(settings, "REQUIRE_LOGIN", True)
        if self.staff_only and not user.is_staff:
            return False
        if self.required_group and not user.is_superuser:
            return user.groups.filter(name=self.required_group).exists()
        return True


class FeatureRegistry:
    def __init__(self):
        self._features: dict[str, Feature] = {}

    def register(self, feature: Feature) -> None:
        self._features[feature.slug] = feature

    def unregister(self, slug: str) -> None:
        self._features.pop(slug, None)

    def for_user(self, user) -> list[Feature]:
        feats = [f for f in self._features.values() if f.visible_to(user)]
        return sorted(feats, key=lambda f: (f.order, f.title))

    def sections_for_user(self, user) -> list[tuple[str, list[Feature]]]:
        """Features grouped by sidebar section, preserving order."""
        grouped: dict[str, list[Feature]] = {}
        for f in self.for_user(user):
            grouped.setdefault(f.section, []).append(f)
        return list(grouped.items())


registry = FeatureRegistry()
