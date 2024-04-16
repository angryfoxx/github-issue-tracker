from celery import Celery

__all__ = ["app"]

app = Celery("gissues")
app.config_from_object("django.conf:settings", namespace="CELERY")
