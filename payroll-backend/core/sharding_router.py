class ShardingRouter:
    """
    A router to control all database operations on models in the
    payroll-backend application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to route read operations based on company context.
        """
        instance = hints.get("instance")
        if instance:
            if model.__name__ == "Company":
                return self._shard_for_company(instance.id)

            # Check for company link in multiple ways
            company_id = getattr(instance, "company_id", None)
            if not company_id:
                company = getattr(instance, "company", None)
                if company:
                    company_id = getattr(company, "id", None)

            if company_id:
                return self._shard_for_company(company_id)
        return "default"

    def db_for_write(self, model, **hints):
        """
        Attempts to route write operations based on company context.
        """
        instance = hints.get("instance")
        if instance:
            if model.__name__ == "Company":
                return self._shard_for_company(instance.id)

            company_id = getattr(instance, "company_id", None)
            if not company_id:
                company = getattr(instance, "company", None)
                if company:
                    company_id = getattr(company, "id", None)

            if company_id:
                return self._shard_for_company(company_id)
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow all relations for this POC to avoid initialization order issues.
        In a production system, you'd want stricter checks, but here
        we rely on db_for_write logic.
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the site_manage app only appears in the shard databases.
        """
        if app_label == "site_manage":
            return db in ["default", "shard2"]
        return True

    def _shard_for_company(self, company_id):
        """
        Deterministic sharding logic.
        In this POC:
        - Even IDs go to 'default'
        - Odd IDs go to 'shard2'
        """
        if company_id % 2 == 0:
            return "default"
        return "shard2"
