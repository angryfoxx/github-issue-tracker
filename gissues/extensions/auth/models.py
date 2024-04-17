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
