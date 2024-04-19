import datetime

from rest_framework.reverse import reverse

import pytest


@pytest.mark.django_db
def test_UserRepositoryFollowViewSet_list(api_client, user, repository_factory, user_repository_follow_factory):
    repository = repository_factory.create()
    user_repository_follow_factory.create(user=user, repository=repository)

    api_client.force_authenticate(user=user)

    response = api_client.get(
        reverse("api:following-repositories-list"),
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"] == [
        {
            "id": repository.id,
            "name": repository.name,
            "owner_name": repository.owner_name,
            "description": repository.description,
            "is_private": repository.is_private,
            "is_fork": repository.is_fork,
            "created_at": datetime.datetime.strftime(repository.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": datetime.datetime.strftime(repository.updated_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "pushed_at": datetime.datetime.strftime(repository.pushed_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        }
    ]
