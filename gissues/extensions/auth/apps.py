from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gissues.extensions.auth"
    label = "account"
    verbose_name = "Account"
