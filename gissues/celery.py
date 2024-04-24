from django.conf import settings
from django.utils import timezone

from celery import Celery

__all__ = ["app"]


app = Celery("gissues")
app.config_from_object("django.conf:settings", namespace="CELERY")

ISSUE_SCHEDULE = {
    "issue-system": {
        "task": "gissues.extensions.github_client.tasks.check_for_new_issues",
        "schedule": timezone.timedelta(minutes=settings.CHECK_FOR_NEW_ISSUES_INTERVAL_IN_MINUTES),
    },
}

app.conf.beat_schedule.update(ISSUE_SCHEDULE)
