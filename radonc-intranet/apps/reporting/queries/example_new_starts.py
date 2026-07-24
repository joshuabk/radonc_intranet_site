"""Template for a live report. Not wired up until its ReportDefinition
row is set to status=live and the 'aria' connection exists."""
from apps.reporting.datasources import run_readonly_query

SQL = """
-- Example shape only; confirm real table/column names against your
-- ARIA version with the Varian DBA before going live.
SELECT TOP 100 PatientId, CourseId, StartDateTime
FROM   <your_view_or_table>
WHERE  StartDateTime >= %s
ORDER  BY StartDateTime
"""


def run(params: dict):
    return run_readonly_query("aria", SQL, [params.get("start_date")])
