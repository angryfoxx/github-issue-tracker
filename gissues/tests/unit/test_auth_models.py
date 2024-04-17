import pytest
from django.db import IntegrityError

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
