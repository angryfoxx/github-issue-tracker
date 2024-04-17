import datetime

import factory

from gissues.extensions.auth.models import User, UserRepositoryFollow
from gissues.extensions.github.models import Comments, Issue, IssueCommentBody, Repository


class RepositoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Repository

    name = factory.Sequence(lambda n: f"repo-{n}")
    owner_name = factory.Faker("user_name")
    description = factory.Faker("sentence")
    is_private = factory.Faker("boolean")
    is_fork = factory.Faker("boolean")

    created_at = factory.Faker("date_time", tzinfo=datetime.timezone.utc)
    updated_at = factory.Faker("date_time", tzinfo=datetime.timezone.utc)
    pushed_at = factory.Faker("date_time", tzinfo=datetime.timezone.utc)


class IssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Issue

    title = factory.Faker("sentence")
    number = factory.Sequence(lambda n: n)
    is_closed = factory.Faker("boolean")
    closed_at = factory.Faker("date_time", tzinfo=datetime.timezone.utc)
    state_reason = factory.Faker("random_element", elements=[x[0] for x in Issue.StateReason.choices])
    is_locked = factory.Faker("boolean")
    lock_reason = factory.Faker("random_element", elements=[x[0] for x in Issue.LockReason.choices])
    repository = factory.SubFactory(RepositoryFactory)

    created_at = factory.Faker("date_time", tzinfo=datetime.timezone.utc)
    updated_at = factory.Faker("date_time", tzinfo=datetime.timezone.utc)


class CommentsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comments

    comment_id = factory.Sequence(lambda n: n)
    issue = factory.SubFactory(IssueFactory)
    created_at = factory.Faker("date_time", tzinfo=datetime.timezone.utc)
    updated_at = factory.Faker("date_time", tzinfo=datetime.timezone.utc)


class IssueCommentBodyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IssueCommentBody

    body = factory.Faker("sentence")
    issue = factory.SubFactory(IssueFactory)
    comment = factory.SubFactory(CommentsFactory)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user-{n}")
    email = factory.Sequence(lambda n: f"user-email{n}@gmail.com")
    password = factory.PostGenerationMethodCall("set_password", "password")

    is_staff = factory.Faker("boolean")
    is_active = factory.Faker("boolean")
    is_superuser = factory.Faker("boolean")

    last_login = factory.Faker("date_time", tzinfo=datetime.timezone.utc)
    date_joined = factory.Faker("date_time", tzinfo=datetime.timezone.utc)


class UserRepositoryFollowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserRepositoryFollow

    user = factory.SubFactory(UserFactory)
    repository = factory.SubFactory(RepositoryFactory)
