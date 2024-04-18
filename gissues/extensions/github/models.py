from django.db import models

from simple_history.models import HistoricalRecords


class Comments(models.Model):
    comment_id = models.PositiveIntegerField(unique=True)
    body = models.TextField(max_length=65536)
    issue = models.ForeignKey("Issue", related_name="comments", on_delete=models.CASCADE)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    history = HistoricalRecords()

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"

    def __str__(self) -> str:
        return f"C{self.comment_id}"


class Issue(models.Model):
    class StateReason(models.TextChoices):
        NOT_PLANNED = "not_planned", "Not planned"
        COMPLETED = "completed", "Completed"
        REOPENED = "reopened", "Reopened"

    class LockReason(models.TextChoices):
        OFF_TOPIC = "off_topic", "Off-topic"
        TOO_HEATED = "too heated", "Too heated"
        RESOLVED = "resolved", "Resolved"
        SPAM = "spam", "Spam"
        OTHER = "other", "Other"

    title = models.CharField(max_length=256)
    number = models.PositiveIntegerField(unique=True)
    body = models.TextField(max_length=65536)
    # the issue is open and state_reason can be null or reopened when the issue is closed
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True)
    state_reason = models.CharField(max_length=11, choices=StateReason.choices, null=True)
    is_locked = models.BooleanField(default=False)
    lock_reason = models.CharField(max_length=10, choices=LockReason.choices, null=True)
    repository = models.ForeignKey("Repository", related_name="issues", on_delete=models.CASCADE)
    comment_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    history = HistoricalRecords()

    class Meta:
        verbose_name = "issue"
        verbose_name_plural = "issues"

    def __str__(self) -> str:
        return self.title


class Repository(models.Model):
    name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=39)
    description = models.CharField(max_length=350)
    is_private = models.BooleanField(default=False)
    is_fork = models.BooleanField(default=False)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    pushed_at = models.DateTimeField()

    history = HistoricalRecords()

    class Meta:
        verbose_name = "repository"
        verbose_name_plural = "repositories"
        constraints = [models.UniqueConstraint(fields=["name", "owner_name"], name="unique_repository")]

    def __str__(self) -> str:
        return self.name
