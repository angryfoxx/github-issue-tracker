# Generated by Django 5.0.4 on 2024-04-18 22:42

import django.db.models.deletion
import django.db.models.functions.text
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("account", "0001_initial"),
        ("github", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userrepositoryfollow",
            name="repository",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="followers", to="github.repository"
            ),
        ),
        migrations.AddField(
            model_name="userrepositoryfollow",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="repositories_followed",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("email"),
                name="unique_lower_email",
                violation_error_message="A user with that e-mail already exists.",
            ),
        ),
        migrations.AddConstraint(
            model_name="userrepositoryfollow",
            constraint=models.UniqueConstraint(fields=("user", "repository"), name="unique_user_repository_follow"),
        ),
    ]