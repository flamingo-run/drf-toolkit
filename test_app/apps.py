from django.apps import AppConfig


class SampleAppConfig(AppConfig):
    name = "test_app"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from test_app import signals  # noqa
