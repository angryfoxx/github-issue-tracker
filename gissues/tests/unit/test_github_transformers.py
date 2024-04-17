import pytest

from gissues.extensions.github.transformers import transform_comments, transform_issue, transform_repository


@pytest.mark.parametrize(
    "repository",
    [
        {
            "name": "gissues",
            "owner": {"login": "gissues"},
            "description": "A Django application to manage GitHub issues.",
            "private": False,
            "fork": False,
            "created_at": "2021-05-25T10:00:00Z",
            "updated_at": "2021-05-25T10:00:00Z",
            "pushed_at": "2021-05-25T10:00:00Z",
        }
    ],
)
def test_transform_repository(repository):
    transformed_repository = transform_repository(repository)
    assert transformed_repository.name == repository["name"]
    assert transformed_repository.owner_name == repository["owner"]["login"]
    assert transformed_repository.description == repository["description"]
    assert transformed_repository.is_private == repository["private"]
    assert transformed_repository.is_fork == repository["fork"]
    assert transformed_repository.created_at == repository["created_at"]
    assert transformed_repository.updated_at == repository["updated_at"]
    assert transformed_repository.pushed_at == repository["pushed_at"]


@pytest.mark.parametrize(
    "issue",
    [
        {
            "title": "Add a new feature",
            "number": 1,
            "state": "open",
            "closed_at": None,
            "state_reason": None,
            "locked": False,
            "active_lock_reason": None,
            "created_at": "2021-05-25T10:00:00Z",
            "updated_at": "2021-05-25T10:00:00Z",
        }
    ],
)
def test_transform_issue_without_repository(issue):
    transformed_issue = transform_issue(issue)
    assert transformed_issue.title == issue["title"]
    assert transformed_issue.number == issue["number"]
    assert transformed_issue.is_closed is False
    assert transformed_issue.closed_at == issue["closed_at"]
    assert transformed_issue.state_reason == issue["state_reason"]
    assert transformed_issue.is_locked == issue["locked"]
    assert transformed_issue.lock_reason == issue["active_lock_reason"]
    assert transformed_issue.repository is None
    assert transformed_issue.created_at == issue["created_at"]
    assert transformed_issue.updated_at == issue["updated_at"]


@pytest.mark.parametrize(
    "issue, repository",
    [
        (
            {
                "title": "Add a new feature",
                "number": 1,
                "state": "open",
                "closed_at": None,
                "state_reason": None,
                "locked": False,
                "active_lock_reason": None,
                "created_at": "2021-05-25T10:00:00Z",
                "updated_at": "2021-05-25T10:00:00Z",
            },
            {
                "name": "gissues",
                "owner": {"login": "gissues"},
                "description": "A Django application to manage GitHub issues.",
                "private": False,
                "fork": False,
                "created_at": "2021-05-25T10:00:00Z",
                "updated_at": "2021-05-25T10:00:00Z",
                "pushed_at": "2021-05-25T10:00:00Z",
            },
        )
    ],
)
def test_transform_issue_with_repository(issue, repository):
    transformed_repository = transform_repository(repository)
    transformed_issue = transform_issue(issue, transformed_repository)
    assert transformed_issue.title == issue["title"]
    assert transformed_issue.number == issue["number"]
    assert transformed_issue.is_closed is False
    assert transformed_issue.closed_at == issue["closed_at"]
    assert transformed_issue.state_reason == issue["state_reason"]
    assert transformed_issue.is_locked == issue["locked"]
    assert transformed_issue.lock_reason == issue["active_lock_reason"]
    assert transformed_issue.repository == transformed_repository
    assert transformed_issue.created_at == issue["created_at"]
    assert transformed_issue.updated_at == issue["updated_at"]


@pytest.mark.parametrize(
    "comment, issue",
    [
        (
            {
                "id": 1,
                "body": "This is a comment",
                "created_at": "2021-05-25T10:00:00Z",
                "updated_at": "2021-05-25T10:00:00Z",
            },
            {
                "title": "Add a new feature",
                "number": 1,
                "state": "open",
                "closed_at": None,
                "state_reason": None,
                "locked": False,
                "active_lock_reason": None,
                "created_at": "2021-05-25T10:00:00Z",
                "updated_at": "2021-05-25T10:00:00Z",
            },
        )
    ],
)
def test_transform_comments(comment, issue):
    transformed_issue = transform_issue(issue)
    transformed_comment = transform_comments(comment, transformed_issue)
    assert transformed_comment.body == comment["body"]
    assert transformed_comment.issue == transformed_issue
    assert transformed_comment.comment.comment_id == comment["id"]
    assert transformed_comment.comment.created_at == comment["created_at"]
    assert transformed_comment.comment.updated_at == comment["updated_at"]
