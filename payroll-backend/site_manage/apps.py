from django.apps import AppConfig


class SiteManageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "site_manage"

    def ready(self):
        # Implicitly load models from infrastructure so Django registries find them
        import site_manage.infrastructure.models  # noqa
