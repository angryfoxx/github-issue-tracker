from django.db import IntegrityError

import pytest

from gissues.extensions.github.models import Comments, Issue, Repository


@pytest.mark.django_db
def test_repository_creation_successful(repository_factory):
    repository = repository_factory.create()
    assert Repository.objects.count() == 1
    assert repository.name == Repository.objects.first().name
    assert repository.owner_name == Repository.objects.first().owner_name
    assert repository.description == Repository.objects.first().description
    assert repository.is_private == Repository.objects.first().is_private
    assert repository.is_fork == Repository.objects.first().is_fork
    assert repository.created_at == Repository.objects.first().created_at
    assert repository.updated_at == Repository.objects.first().updated_at
    assert repository.pushed_at == Repository.objects.first().pushed_at
    assert str(repository) == repository.name


@pytest.mark.django_db
def test_repository_creation_with_already_existing_name(repository_factory):
    first_repo = repository_factory.create()

    second_repo = repository_factory.build(name=first_repo.name, owner_name=first_repo.owner_name)

    with pytest.raises(IntegrityError):
        second_repo.save()


@pytest.mark.django_db
def test_repository_history(repository_factory):
    repository = repository_factory.create()
    assert repository.history.count() == 1
    assert repository.history.first().history_user is None
    assert repository.history.first().history_type == "+"
    assert repository.history.first().history_change_reason is None
    assert repository.history.first().name == repository.name
    assert repository.history.first().owner_name == repository.owner_name
    assert repository.history.first().description == repository.description
    assert repository.history.first().is_private == repository.is_private
    assert repository.history.first().is_fork == repository.is_fork
    assert repository.history.first().created_at == repository.created_at
    assert repository.history.first().updated_at == repository.updated_at
    assert repository.history.first().pushed_at == repository.pushed_at


@pytest.mark.django_db
def test_issue_creation_successful(issue_factory):
    issue = issue_factory.create()
    assert Issue.objects.count() == 1
    assert issue.title == Issue.objects.first().title
    assert issue.number == Issue.objects.first().number
    assert issue.is_closed == Issue.objects.first().is_closed
    assert issue.closed_at == Issue.objects.first().closed_at
    assert issue.state_reason == Issue.objects.first().state_reason
    assert issue.is_locked == Issue.objects.first().is_locked
    assert issue.lock_reason == Issue.objects.first().lock_reason
    assert issue.repository == Issue.objects.first().repository
    assert issue.created_at == Issue.objects.first().created_at
    assert issue.updated_at == Issue.objects.first().updated_at
    assert str(issue) == issue.title


@pytest.mark.django_db
def test_issue_creation_with_already_existing_number(issue_factory):
    first_issue = issue_factory.create()

    second_issue = issue_factory.build(number=first_issue.number, repository=first_issue.repository)

    with pytest.raises(IntegrityError):
        second_issue.save()


@pytest.mark.django_db
def test_issue_history(issue_factory):
    issue = issue_factory.create()
    assert issue.history.count() == 1
    assert issue.history.first().history_user is None
    assert issue.history.first().history_type == "+"
    assert issue.history.first().history_change_reason is None
    assert issue.history.first().title == issue.title
    assert issue.history.first().number == issue.number
    assert issue.history.first().is_closed == issue.is_closed
    assert issue.history.first().closed_at == issue.closed_at
    assert issue.history.first().state_reason == issue.state_reason
    assert issue.history.first().is_locked == issue.is_locked
    assert issue.history.first().lock_reason == issue.lock_reason
    assert issue.history.first().repository == issue.repository
    assert issue.history.first().created_at == issue.created_at
    assert issue.history.first().updated_at == issue.updated_at


@pytest.mark.django_db
def test_comments_creation_successful(comments_factory):
    comments = comments_factory.create()
    assert Comments.objects.count() == 1
    assert comments.comment_id == Comments.objects.first().comment_id
    assert comments.issue == Comments.objects.first().issue
    assert comments.created_at == Comments.objects.first().created_at
    assert comments.updated_at == Comments.objects.first().updated_at
    assert str(comments) == f"C{comments.comment_id}"


@pytest.mark.django_db
def test_comments_creation_with_already_existing_comment_id(comments_factory):
    first_comments = comments_factory.create()

    second_comments = comments_factory.build(comment_id=first_comments.comment_id, issue=first_comments.issue)

    with pytest.raises(IntegrityError):
        second_comments.save()


@pytest.mark.django_db
def test_comments_history(comments_factory):
    comments = comments_factory.create()
    assert comments.history.count() == 1
    assert comments.history.first().history_user is None
    assert comments.history.first().history_type == "+"
    assert comments.history.first().history_change_reason is None
    assert comments.history.first().comment_id == comments.comment_id
    assert comments.history.first().issue == comments.issue
    assert comments.history.first().created_at == comments.created_at
    assert comments.history.first().updated_at == comments.updated_at
