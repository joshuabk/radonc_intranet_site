class ClinicalSystemRouter:
    """Keeps Django from ever migrating or writing to ARIA/MOSAIQ.

    Those aliases are read-only reporting connections; all application data
    lives in 'default'.
    """

    CLINICAL_ALIASES = {"aria", "mosaiq"}

    def db_for_read(self, model, **hints):
        return None  # default behavior; reporting queries pick their alias explicitly

    def db_for_write(self, model, **hints):
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db in self.CLINICAL_ALIASES:
            return False
        return None
