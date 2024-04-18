from dataclasses import dataclass
from unittest.mock import patch

from django.http import Http404

import pytest

from gissues.extensions.github.dataclasses import BaseDataclass
from gissues.extensions.github.models import Issue, Repository
from gissues.extensions.github.transformers import transform_comments, transform_issue, transform_repository


def test_base_dataclass_dict():
    @dataclass
    class Test(BaseDataclass):
        name: str
        age: int

    test = Test(name="John", age=30)
    assert test.dict() == {"name": "John", "age": 30}


def test_transform_repository():
    repository = {
        "name": "gissues",
        "owner": {"login": "gissues"},
        "description": "A Django application to manage GitHub issues.",
        "private": False,
        "fork": False,
        "created_at": "2021-05-25T10:00:00Z",
        "updated_at": "2021-05-25T10:00:00Z",
        "pushed_at": "2021-05-25T10:00:00Z",
    }
    transformed_repository = transform_repository(repository)
    assert transformed_repository.name == repository["name"]
    assert transformed_repository.owner_name == repository["owner"]["login"]
    assert transformed_repository.description == repository["description"]
    assert transformed_repository.is_private == repository["private"]
    assert transformed_repository.is_fork == repository["fork"]
    assert transformed_repository.created_at == repository["created_at"]
    assert transformed_repository.updated_at == repository["updated_at"]
    assert transformed_repository.pushed_at == repository["pushed_at"]


@patch("gissues.extensions.github.transformers.get_object_or_404")
@pytest.mark.django_db
def test_transform_issue(mock_get_object_or_404, repository_factory):
    repository = repository_factory.create()

    mock_get_object_or_404.return_value = repository

    issue = {
        "title": "Add a new feature",
        "number": 1,
        "body": "This is a new feature.",
        "state": "open",
        "closed_at": None,
        "state_reason": None,
        "locked": False,
        "active_lock_reason": None,
        "created_at": "2021-05-25T10:00:00Z",
        "updated_at": "2021-05-25T10:00:00Z",
    }
    transformed_issue = transform_issue(
        issue,
        repository.name,
        repository.owner_name,
    )
    assert transformed_issue.title == issue["title"]
    assert transformed_issue.number == issue["number"]
    assert transformed_issue.body == issue["body"]
    assert transformed_issue.is_closed is False
    assert transformed_issue.closed_at == issue["closed_at"]
    assert transformed_issue.state_reason == issue["state_reason"]
    assert transformed_issue.is_locked == issue["locked"]
    assert transformed_issue.lock_reason == issue["active_lock_reason"]
    assert transformed_issue.repository == repository
    assert transformed_issue.created_at == issue["created_at"]
    assert transformed_issue.updated_at == issue["updated_at"]

    mock_get_object_or_404.assert_called_once_with(Repository, name=repository.name, owner_name=repository.owner_name)


@patch("gissues.extensions.github.transformers.get_object_or_404")
@pytest.mark.django_db
def test_transform_comments(mock_get_object_or_404, issue_factory):
    issue = issue_factory.create()

    mock_get_object_or_404.return_value = issue

    comment = {
        "id": 1,
        "body": "This is a comment",
        "created_at": "2021-05-25T10:00:00Z",
        "updated_at": "2021-05-25T10:00:00Z",
    }
    transformed_comment = transform_comments(comment, issue.number)
    assert transformed_comment.body == comment["body"]
    assert transformed_comment.issue == issue
    assert transformed_comment.comment_id == comment["id"]
    assert transformed_comment.created_at == comment["created_at"]
    assert transformed_comment.updated_at == comment["updated_at"]

    mock_get_object_or_404.assert_called_once_with(Issue, number=issue.number)


@patch("gissues.extensions.github.transformers.get_object_or_404")
@pytest.mark.django_db
@pytest.mark.parametrize(
    "func, model, func_args, get_object_or_404_kwargs",
    [
        (
            transform_issue,
            Repository,
            {"issue": {}, "repository_name": "gissues", "owner_name": "gissues"},
            {"name": "gissues", "owner_name": "gissues"},
        ),
        (transform_comments, Issue, {"comment": {}, "issue_number": 1}, {"number": 1}),
    ],
)
def test_transformers_with_http404(mock_get_object_or_404, func, model, func_args, get_object_or_404_kwargs):
    mock_get_object_or_404.side_effect = Http404

    with pytest.raises(Http404):
        func(**func_args)

    mock_get_object_or_404.assert_called_once_with(model, **get_object_or_404_kwargs)
