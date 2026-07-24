"""
Read-only access layer for clinical system databases.

Reports never open their own connections; they call run_readonly_query()
so that (a) access is uniform, (b) every query can be audited, and
(c) it is impossible to forget the read-only intent.

To bring a source online:
  1. Have the Varian/Elekta DBA provision a READ-ONLY SQL login.
  2. Set ARIA_DB_* / MOSAIQ_DB_* environment variables (see .env.example).
  3. pip install mssql-django pyodbc (and the MS ODBC driver on the server).
  4. Flip the relevant ReportDefinition rows to status=live.
"""
from django.conf import settings
from django.db import connections


class DataSourceNotConfigured(Exception):
    pass


def source_is_configured(alias: str) -> bool:
    return alias in settings.DATABASES


def run_readonly_query(alias: str, sql: str, params=None, max_rows: int = 5000):
    """Execute a parameterized SELECT against a clinical DB alias.

    Returns (columns, rows). Raises DataSourceNotConfigured when the
    connection has not been set up yet, so views can show a friendly
    'not yet connected' state instead of a 500.
    """
    if not source_is_configured(alias):
        raise DataSourceNotConfigured(
            f"The '{alias}' database connection is not configured on this server."
        )
    sql_stripped = sql.lstrip().lower()
    if not (sql_stripped.startswith("select") or sql_stripped.startswith("with")):
        raise ValueError("Only SELECT queries are permitted against clinical systems.")

    with connections[alias].cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [c[0] for c in cursor.description] if cursor.description else []
        rows = cursor.fetchmany(max_rows)
    return columns, rows
