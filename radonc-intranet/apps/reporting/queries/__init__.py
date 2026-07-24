"""
One module per live report, named after the ReportDefinition slug.

Each module exposes:

    def run(params: dict) -> tuple[list[str], list[tuple]]:
        from apps.reporting.datasources import run_readonly_query
        return run_readonly_query("aria", "SELECT ...", [params["start"]])

See queries/example_new_starts.py for a worked template.
"""
