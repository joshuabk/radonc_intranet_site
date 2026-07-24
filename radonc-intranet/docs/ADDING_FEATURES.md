# Adding a New Large Feature

The site is built so a new feature is a self-contained Django app that announces itself to the rest of the site through the **feature registry**. The sidebar nav, home-page tiles, and (optionally) group gating all come from the registration — you never edit `base.html`.

## 1. Create the app

```bash
python manage.py startapp qa apps/qa     # example: a machine QA tracking feature
```

Set the app config name in `apps/qa/apps.py`:

```python
from django.apps import AppConfig

class QaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.qa"

    def ready(self):
        from apps.core.registry import Feature, registry
        registry.register(Feature(
            slug="qa",
            title="Machine QA",
            description="Daily/monthly QA status and trends.",
            url_name="qa:home",          # namespaced URL of the landing page
            icon="monitor",               # key from templates/core/_icons.html
            order=60,                     # sidebar/tile sort position
            section="Clinical",          # sidebar group heading
            required_group=None,          # or e.g. "Physics" to gate + hide nav
        ))
```

## 2. Register it

- Add `"apps.qa"` to `INSTALLED_APPS` in `config/settings/base.py`.
- Add `path("qa/", include("apps.qa.urls", namespace="qa"))` to `config/urls.py`.
- Give `apps/qa/urls.py` an `app_name = "qa"` and a `home` route.

## 3. Build the pages

Extend the shared layout and you inherit the sidebar, search, announcements, and styling:

```html
{% extends "base.html" %}
{% block title %}Machine QA{% endblock %}
{% block content %}
  <div class="page-head"><h1>Machine QA</h1></div>
  ...
{% endblock %}
```

Use the existing CSS classes (`card`, `table`, `badge`, `btn`, `page-head`) in `static/css/app.css` before writing new ones — they cover most layouts.

## 4. Optional pieces

- **Group gating:** set `required_group="Physics"` in the Feature; also enforce in views with `@user_passes_test` (see `apps/reporting/views.py` for the pattern). The registry handles hiding the nav; the decorator handles the actual security.
- **Sub-navigation:** pass `nav_items=[("qa:daily", "Daily QA"), ("qa:trends", "Trends")]` to `Feature` for sidebar sub-links.
- **Icons:** add a new `<symbol>` to `templates/core/_icons.html` (inline SVG, no external requests).
- **Home tile:** automatic — every registered feature gets a tile unless the user lacks its `required_group`.
- **Search:** add your models to `apps/core/views.py::search` if they should appear in global search.

## 5. Migrate and test

```bash
python manage.py makemigrations qa && python manage.py migrate
python manage.py test
```

Follow the test style in `apps/core/tests.py` (login required, page renders, gating works).
