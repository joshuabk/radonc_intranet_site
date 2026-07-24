# RadOnc Intranet

A Django framework application for a radiation oncology department intranet, designed to run on an internal hospital network. It ships with a working shell for each planned feature and a registry pattern that makes adding large new features straightforward.

## Features (framework shells, ready to build out)

| Feature | URL | What's there now |
|---|---|---|
| Link Hub | `/links/` | Categorized links to ARIA, MOSAIQ, Citrix, SharePoint, LucidDoc, forms, reports. UNC paths (P-drive) get a copy-to-clipboard button instead of a dead link. Pinned links appear on the home page. |
| Service Contacts | `/contacts/` | Engineer / vendor / internal contact directory with systems covered, locations, after-hours numbers, and support portal links. Searchable. |
| Coverage | `/coverage/` | Current and upcoming coverage assignments (clinical, on-call, HDR, specials), plus links out to PTO / on-call calendars (Outlook, QGenda, etc.). |
| Coverage Matrix | `/coverage/matrix/` | Physicist × procedure grid (primary / backup / training) filterable by location, with credential expiry tracking on each capability. |
| Huddle Board | `/huddle/` | New starts (today + next 7 days) and special procedures, with a wall-monitor display mode (`?display=1`), auto-refresh, and print styles. |
| Reporting | `/reports/` | Group-gated (`Reporting Access`) report list with read-only ARIA / MOSAIQ database plumbing already wired (disabled until configured). See `docs/REPORTING.md`. |

Everything requires login (site-wide `LoginRequiredMiddleware`). No external CDNs — all CSS, JS, and icons are local, so it works on an isolated network.

## Quick start (development)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py bootstrap_site      # creates the standard groups
python manage.py seed_demo           # optional: fictional demo data
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000/ and log in. Manage content at `/admin/`.

## Project layout

```
config/
  settings/base.py      shared settings, SITE_GROUPS, feature flags
  settings/dev.py       DEBUG, sqlite
  settings/prod.py      env-driven, whitenoise, security headers
apps/
  core/                 home, search, announcements, feature registry
  linkhub/              link hub
  contacts/             service engineer directory
  coverage/             assignments, calendars, capability matrix
  huddle/               new starts + specials dashboard
  reporting/            gated reports, ARIA/MOSAIQ read-only plumbing
templates/              base layout + per-app templates
static/                 css/app.css design system, js/app.js, icons
docs/                   ADDING_FEATURES, AUTHENTICATION, REPORTING
```

## Adding a new large feature

The sidebar navigation and home-page tiles are generated from a **feature registry**. A new app registers itself in its `AppConfig.ready()` and appears everywhere automatically — no template edits. Full walkthrough in `docs/ADDING_FEATURES.md`.

## Groups and access

`bootstrap_site` creates: **Physics, Dosimetry, Therapists, Reporting Access, Content Admins**. The reporting section is restricted to `Reporting Access`; the nav link is hidden for everyone else. Hook this to Active Directory later via LDAP — see `docs/AUTHENTICATION.md`.

## Production deployment (internal network)

1. Copy `.env.example` to `.env` and set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` (e.g. `radonc.hospital.local`), and database settings.
2. Use `config.settings.prod` (the default for `wsgi.py` / `asgi.py`).
3. `python manage.py collectstatic` — whitenoise serves static files; no separate web server config needed for them.
4. Serve with **waitress** (simple on Windows servers) or **gunicorn** (Linux):
   ```bash
   # Windows
   waitress-serve --listen=0.0.0.0:8000 config.wsgi:application
   # Linux
   gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```
5. Put IIS (ARR reverse proxy) or nginx in front if you need TLS or a friendly hostname.
6. For real usage, switch the default database from SQLite to SQL Server or PostgreSQL (commented drivers in `requirements.txt`).

If the site stays HTTP-only on the internal network, the `SECURE_*` deploy warnings are expected; enable them via env vars when you put TLS in front.

## PHI note

The huddle board stores MRN + treatment site only (minimum necessary). The whole site is behind login, but review your organization's policies before adding more patient detail, and prefer AD-backed auth (`docs/AUTHENTICATION.md`) before go-live.
