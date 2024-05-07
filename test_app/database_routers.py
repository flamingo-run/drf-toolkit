class FeatureRouter:
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in {"reservation"}:  # PSQL-only
            return db == "default"
        return True
