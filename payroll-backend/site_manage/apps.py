from django.apps import AppConfig


class SiteManageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "site_manage"

    def ready(self):
        import site_manage.signals
