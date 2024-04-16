from django.apps import AppConfig


class RestFrameworkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gissues.extensions.rest_framework"
    label = "gissues_rest_framework"
    verbose_name = "Rest Framework"
