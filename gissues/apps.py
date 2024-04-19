from django.apps import AppConfig

import gissues.celery


class GissuesConfig(AppConfig):
    name = "gissues"
    verbose_name = "GitHub Issues"

    def ready(self) -> None:
        gissues.celery.app.autodiscover_tasks(force=True)
