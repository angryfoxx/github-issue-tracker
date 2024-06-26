# Generated by Django 5.0.4 on 2024-04-18 22:42

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Issue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=256)),
                ("number", models.PositiveIntegerField(unique=True)),
                ("body", models.TextField(max_length=65536)),
                ("is_closed", models.BooleanField(default=False)),
                ("closed_at", models.DateTimeField(null=True)),
                (
                    "state_reason",
                    models.CharField(
                        choices=[("not_planned", "Not planned"), ("completed", "Completed"), ("reopened", "Reopened")],
                        max_length=11,
                        null=True,
                    ),
                ),
                ("is_locked", models.BooleanField(default=False)),
                (
                    "lock_reason",
                    models.CharField(
                        choices=[
                            ("off_topic", "Off-topic"),
                            ("too heated", "Too heated"),
                            ("resolved", "Resolved"),
                            ("spam", "Spam"),
                            ("other", "Other"),
                        ],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("comment_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
            ],
            options={
                "verbose_name": "issue",
                "verbose_name_plural": "issues",
            },
        ),
        migrations.CreateModel(
            name="Repository",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("owner_name", models.CharField(max_length=39)),
                ("description", models.CharField(max_length=350)),
                ("is_private", models.BooleanField(default=False)),
                ("is_fork", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                ("pushed_at", models.DateTimeField()),
            ],
            options={
                "verbose_name": "repository",
                "verbose_name_plural": "repositories",
            },
        ),
        migrations.CreateModel(
            name="HistoricalIssue",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("title", models.CharField(max_length=256)),
                ("number", models.PositiveIntegerField(db_index=True)),
                ("body", models.TextField(max_length=65536)),
                ("is_closed", models.BooleanField(default=False)),
                ("closed_at", models.DateTimeField(null=True)),
                (
                    "state_reason",
                    models.CharField(
                        choices=[("not_planned", "Not planned"), ("completed", "Completed"), ("reopened", "Reopened")],
                        max_length=11,
                        null=True,
                    ),
                ),
                ("is_locked", models.BooleanField(default=False)),
                (
                    "lock_reason",
                    models.CharField(
                        choices=[
                            ("off_topic", "Off-topic"),
                            ("too heated", "Too heated"),
                            ("resolved", "Resolved"),
                            ("spam", "Spam"),
                            ("other", "Other"),
                        ],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("comment_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical issue",
                "verbose_name_plural": "historical issues",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalRepository",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("owner_name", models.CharField(max_length=39)),
                ("description", models.CharField(max_length=350)),
                ("is_private", models.BooleanField(default=False)),
                ("is_fork", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                ("pushed_at", models.DateTimeField()),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical repository",
                "verbose_name_plural": "historical repositories",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalComments",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("comment_id", models.PositiveIntegerField(db_index=True)),
                ("body", models.TextField(max_length=65536)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "issue",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="github.issue",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical comment",
                "verbose_name_plural": "historical comments",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Comments",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment_id", models.PositiveIntegerField(unique=True)),
                ("body", models.TextField(max_length=65536)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                (
                    "issue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="comments", to="github.issue"
                    ),
                ),
            ],
            options={
                "verbose_name": "comment",
                "verbose_name_plural": "comments",
            },
        ),
        migrations.AddConstraint(
            model_name="repository",
            constraint=models.UniqueConstraint(fields=("name", "owner_name"), name="unique_repository"),
        ),
        migrations.AddField(
            model_name="issue",
            name="repository",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="issues", to="github.repository"
            ),
        ),
        migrations.AddField(
            model_name="historicalissue",
            name="repository",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="github.repository",
            ),
        ),
    ]
