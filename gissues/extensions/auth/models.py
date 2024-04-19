from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower


class User(AbstractUser):
    email = models.EmailField(
        "e-mail",
        unique=True,
        help_text="Required. 254 characters or fewer.",
        error_messages={
            "unique": "A user with that e-mail already exists.",
        },
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="unique_lower_email",
                violation_error_message="A user with that e-mail already exists.",
            ),
        ]

    def __str__(self) -> str:
        return self.username


class UserRepositoryFollow(models.Model):
    user = models.ForeignKey(User, related_name="repositories_followed", on_delete=models.CASCADE)
    repository = models.ForeignKey("github.Repository", related_name="followers", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User repository follow"
        verbose_name_plural = "User repository follows"
        constraints = [
            models.UniqueConstraint(fields=["user", "repository"], name="unique_user_repository_follow"),
        ]

    def __str__(self) -> str:
        return f"{self.user} follows {self.repository}"
