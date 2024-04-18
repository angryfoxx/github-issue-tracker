import datetime
from unittest.mock import Mock, patch

from rest_framework.reverse import reverse

import pytest

from gissues.extensions.github_client.client import GitHubResponse


@pytest.mark.django_db
def test_RepositoryViewSet_list(api_client, repository_factory):
    repo = repository_factory.create()

    response = api_client.get(reverse("repository-list", kwargs={"repository_owner": repo.owner_name}))

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"] == [
        {
            "id": repo.id,
            "name": repo.name,
            "owner_name": repo.owner_name,
            "description": repo.description,
            "is_private": repo.is_private,
            "is_fork": repo.is_fork,
            "created_at": datetime.datetime.strftime(repo.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": datetime.datetime.strftime(repo.updated_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "pushed_at": datetime.datetime.strftime(repo.pushed_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        },
    ]


@pytest.mark.django_db
def test_RepositoryViewSet_retrieve_with_already_existing_repository(api_client, repository_factory):
    repo = repository_factory.create()

    response = api_client.get(
        reverse("repository-detail", kwargs={"repository_owner": repo.owner_name, "repository_name": repo.name})
    )
    assert response.status_code == 200
    assert response.data == {
        "id": repo.id,
        "name": repo.name,
        "owner_name": repo.owner_name,
        "description": repo.description,
        "is_private": repo.is_private,
        "is_fork": repo.is_fork,
        "created_at": datetime.datetime.strftime(repo.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated_at": datetime.datetime.strftime(repo.updated_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        "pushed_at": datetime.datetime.strftime(repo.pushed_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
    }


@patch("gissues.extensions.github.views.github_client")
@pytest.mark.django_db
def test_RepositoryViewSet_retrieve_with_non_existing_repository(mock_client, api_client):
    repo = {
        "name": "gissues",
        "owner": {"login": "gissues"},
        "description": "A Django application to manage GitHub issues.",
        "private": False,
        "fork": False,
        "created_at": "2021-05-25T10:00:00Z",
        "updated_at": "2021-05-25T10:00:00Z",
        "pushed_at": "2021-05-25T10:00:00Z",
    }

    mock_detail = Mock(spec=GitHubResponse, is_ok=True, content=repo, status_code=200)
    mock_client.repositories.detail.return_value = mock_detail

    response = api_client.get(
        reverse(
            "repository-detail",
            kwargs={"repository_owner": "gissues", "repository_name": "gissues"},
        )
    )

    response_data = response.data
    # Remove the id field from the response data to avoid mismatch
    response_data.pop("id")

    assert response.status_code == 200
    assert response.data == {
        "name": "gissues",
        "owner_name": "gissues",
        "description": "A Django application to manage GitHub issues.",
        "is_private": False,
        "is_fork": False,
        "created_at": "2021-05-25T10:00:00Z",
        "updated_at": "2021-05-25T10:00:00Z",
        "pushed_at": "2021-05-25T10:00:00Z",
    }

    mock_client.repositories.detail.assert_called_once_with(owner="gissues", repository_name="gissues")


@pytest.mark.django_db
def test_IssueViewSet_list(api_client, issue_factory, issue_comment_body_factory):
    issue = issue_factory.create()
    body = issue_comment_body_factory.create(issue=issue)

    response = api_client.get(
        reverse(
            "repository-issues-list",
            kwargs={
                "repository_owner": issue.repository.owner_name,
                "repository_repository_name": issue.repository.name,
            },
        )
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"] == [
        {
            "id": issue.id,
            "title": issue.title,
            "number": issue.number,
            "body": body.body,
            "is_closed": issue.is_closed,
            "closed_at": datetime.datetime.strftime(issue.closed_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "state_reason": issue.state_reason,
            "is_locked": issue.is_locked,
            "lock_reason": issue.lock_reason,
            "created_at": datetime.datetime.strftime(issue.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": datetime.datetime.strftime(issue.updated_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        },
    ]


@pytest.mark.django_db
def test_IssueViewSet_retrieve_with_already_existing_issue(api_client, issue_factory, issue_comment_body_factory):
    issue = issue_factory.create()
    body = issue_comment_body_factory.create(issue=issue)

    response = api_client.get(
        reverse(
            "repository-issues-detail",
            kwargs={
                "repository_owner": issue.repository.owner_name,
                "repository_repository_name": issue.repository.name,
                "issue_number": issue.number,
            },
        )
    )
    assert response.status_code == 200
    assert response.data == {
        "id": issue.id,
        "title": issue.title,
        "number": issue.number,
        "body": body.body,
        "is_closed": issue.is_closed,
        "closed_at": datetime.datetime.strftime(issue.closed_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        "state_reason": issue.state_reason,
        "is_locked": issue.is_locked,
        "lock_reason": issue.lock_reason,
        "created_at": datetime.datetime.strftime(issue.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated_at": datetime.datetime.strftime(issue.updated_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
    }


@patch("gissues.extensions.github.views.github_client")
@pytest.mark.django_db
def test_IssueViewSet_retrieve_with_non_existing_issue(mock_client, api_client, repository_factory):
    repo = repository_factory.create()
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

    mock_detail = Mock(spec=GitHubResponse, is_ok=True, content=issue, status_code=200)
    mock_client.issues.detail.return_value = mock_detail

    response = api_client.get(
        reverse(
            "repository-issues-detail",
            kwargs={"repository_owner": repo.owner_name, "repository_repository_name": repo.name, "issue_number": "1"},
        )
    )

    response_data = response.data
    # Remove the id field from the response data to avoid mismatch
    response_data.pop("id")

    assert response.status_code == 200
    assert response.data == {
        "title": "Add a new feature",
        "number": 1,
        "body": "This is a new feature.",
        "is_closed": False,
        "closed_at": None,
        "state_reason": None,
        "is_locked": False,
        "lock_reason": None,
        "created_at": "2021-05-25T10:00:00Z",
        "updated_at": "2021-05-25T10:00:00Z",
    }

    mock_client.issues.detail.assert_called_once_with(
        owner=repo.owner_name, repository_name=repo.name, issue_number="1"
    )


@pytest.mark.django_db
def test_CommentsViewSet_list(api_client, comments_factory, issue_comment_body_factory):
    comment = comments_factory.create()
    body = issue_comment_body_factory.create(comment=comment)

    response = api_client.get(
        reverse(
            "issue-comments-list",
            kwargs={
                "repository_owner": comment.issue.repository.owner_name,
                "repository_repository_name": comment.issue.repository.name,
                "issue_issue_number": comment.issue.number,
            },
        )
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"] == [
        {
            "id": comment.id,
            "comment_id": comment.comment_id,
            "body": body.body,
            "created_at": datetime.datetime.strftime(comment.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": datetime.datetime.strftime(comment.updated_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        },
    ]


@pytest.mark.django_db
def test_CommentsViewSet_retrieve_with_already_existing_comment(
    api_client, comments_factory, issue_comment_body_factory
):
    comment = comments_factory.create()
    body = issue_comment_body_factory.create(comment=comment)

    response = api_client.get(
        reverse(
            "issue-comments-detail",
            kwargs={
                "repository_owner": comment.issue.repository.owner_name,
                "repository_repository_name": comment.issue.repository.name,
                "issue_issue_number": comment.issue.number,
                "comment_id": comment.comment_id,
            },
        )
    )
    assert response.status_code == 200
    assert response.data == {
        "id": comment.id,
        "comment_id": comment.comment_id,
        "body": body.body,
        "created_at": datetime.datetime.strftime(comment.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated_at": datetime.datetime.strftime(comment.updated_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
    }


@patch("gissues.extensions.github.views.github_client")
@pytest.mark.django_db
def test_CommentsViewSet_retrieve_with_non_existing_comment(mock_client, api_client, issue_factory):
    issue = issue_factory.create()
    comment_data = {
        "id": 1,
        "body": "This is a new comment",
        "created_at": "2021-05-25T10:00:00Z",
        "updated_at": "2021-05-25T10:00:00Z",
    }

    mock_detail = Mock(spec=GitHubResponse, is_ok=True, content=comment_data, status_code=200)
    mock_client.comments.detail.return_value = mock_detail

    response = api_client.get(
        reverse(
            "issue-comments-detail",
            kwargs={
                "repository_owner": issue.repository.owner_name,
                "repository_repository_name": issue.repository.name,
                "issue_issue_number": issue.number,
                "comment_id": "1",
            },
        )
    )

    response_data = response.data
    # Remove the id field from the response data to avoid mismatch
    response_data.pop("id")

    assert response.status_code == 200
    assert response.data == {
        "comment_id": 1,
        "body": "This is a new comment",
        "created_at": "2021-05-25T10:00:00Z",
        "updated_at": "2021-05-25T10:00:00Z",
    }

    mock_client.comments.detail.assert_called_once_with(
        owner=issue.repository.owner_name,
        repository_name=issue.repository.name,
        comment_id="1",
    )