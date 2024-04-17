from django.db import IntegrityError

import pytest

from gissues.extensions.auth.models import User


@pytest.mark.django_db
def test_user_creation_successful(user_factory):
    user = user_factory.create()
    assert User.objects.count() == 1
    assert user.username == User.objects.first().username
    assert user.email == User.objects.first().email
    assert user.first_name == User.objects.first().first_name
    assert user.last_name == User.objects.first().last_name
    assert str(user) == user.username


@pytest.mark.django_db
def test_user_creation_with_already_existing_email(user_factory):
    first_user = user_factory.create()

    second_user = user_factory.build(email=first_user.email)

    with pytest.raises(IntegrityError):
        second_user.save()


@pytest.mark.django_db
def test_user_creation_with_already_existing_username(user_factory):
    first_user = user_factory.create()

    second_user = user_factory.build(username=first_user.username)

    with pytest.raises(IntegrityError):
        second_user.save()


@pytest.mark.django_db
def test_user_repository_follow_creation_successful(user_repository_follow_factory):
    user_repository_follow = user_repository_follow_factory.create()
    assert User.objects.count() == 1
    assert user_repository_follow.user == User.objects.first()
    assert user_repository_follow.repository == user_repository_follow.repository
    assert str(user_repository_follow) == f"{user_repository_follow.user} -> {user_repository_follow.repository}"


@pytest.mark.django_db
def test_user_repository_follow_creation_with_already_existing_user_and_repository(user_repository_follow_factory):
    first_user_repository_follow = user_repository_follow_factory.create()

    second_user_repository_follow = user_repository_follow_factory.build(
        user=first_user_repository_follow.user, repository=first_user_repository_follow.repository
    )

    with pytest.raises(IntegrityError):
        second_user_repository_follow.save()
