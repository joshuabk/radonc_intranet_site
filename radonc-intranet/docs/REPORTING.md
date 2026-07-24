# Reporting: ARIA & MOSAIQ Read-Only Connections

The reporting app is wired so that ARIA and MOSAIQ become available as **read-only** Django database aliases the moment you set environment variables. Until then, the reports page shows a friendly "not configured" state instead of erroring.

## How it's protected

- `apps/reporting/routers.py::ClinicalSystemRouter` refuses migrations and writes on the `aria` and `mosaiq` aliases.
- `apps/reporting/datasources.py::run_readonly_query()` only executes statements that begin with `SELECT` (or `WITH`), with parameterized arguments.
- The whole section requires the **Reporting Access** group; every execution is logged to the `ReportRun` audit table (who, what, when, row count, duration).
- **Strongly recommended:** the SQL login you use should itself be read-only (`db_datareader` only) on the vendor databases. The app-level guards are a second layer, not a substitute.

## Enabling the connections

1. Uncomment `mssql-django` and `pyodbc` in `requirements.txt` and install (requires the Microsoft ODBC Driver 17/18 for SQL Server on the host).

2. Set environment variables (see `.env.example`):

```
ARIA_DB_HOST=ariadb.hospital.local
ARIA_DB_NAME=VARIAN
ARIA_DB_USER=radonc_ro
ARIA_DB_PASSWORD=...
MOSAIQ_DB_HOST=mosaiqdb.hospital.local
MOSAIQ_DB_NAME=MOSAIQ
MOSAIQ_DB_USER=radonc_ro
MOSAIQ_DB_PASSWORD=...
```

`config/settings/base.py` adds the `aria` / `mosaiq` entries to `DATABASES` only when the host variable is present, so dev machines work without any of this.

3. Restart the app. The status dots on `/reports/` turn green when a connection test succeeds.

## Writing a report

1. Create a query module, e.g. `apps/reporting/queries/new_starts_aria.py`:

```python
TITLE = "New starts this week (ARIA)"
DATABASE = "aria"

SQL = """
SELECT TOP 100 pt.PatientId, cs.StartDateTime
FROM ...
WHERE cs.StartDateTime >= %s
ORDER BY cs.StartDateTime
"""

def get_params(request):
    from datetime import date, timedelta
    return [date.today() - timedelta(days=7)]
```

2. In `/admin/`, add a **Report Definition** with slug `new_starts_aria`, pick the data source, and mark it active. It appears on `/reports/` for the Reporting Access group; the detail page runs it and renders the result table.

Vendor schemas (ARIA's `VARIAN` DB, MOSAIQ's tables) are proprietary — build queries with your Varian/Elekta support resources or existing report SQL your team already trusts. Keep result sets to the minimum necessary PHI.
