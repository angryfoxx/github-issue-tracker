from rest_framework.generics import get_object_or_404

from gissues.extensions.github.dataclasses import CommentsDataclass, IssueDataclass, RepositoryDataclass
from gissues.extensions.github.models import Issue, Repository


def transform_repository(repository: dict) -> RepositoryDataclass:
    """Transforms a GitHub repository to a dictionary with the required fields.

    Args:
        repository (dict): The GitHub repository to transform.

    Returns:
        RepositoryDataclass: The transformed GitHub repository.
    """
    return RepositoryDataclass(
        name=repository["name"],
        owner_name=repository["owner"]["login"],
        description=repository["description"],
        is_private=repository["private"],
        is_fork=repository["fork"],
        created_at=repository["created_at"],
        updated_at=repository["updated_at"],
        pushed_at=repository["pushed_at"],
    )


def transform_issue(issue: dict, repository_name: str) -> IssueDataclass:
    """Transforms a GitHub issue to a dictionary with the required fields.

    Args:
        issue (dict): The GitHub issue to transform.
        repository_name (str): The repository name where the issue belongs.

    Returns:
        IssueDataclass: The transformed GitHub issue.
    """

    repository = get_object_or_404(Repository, name=repository_name)

    return IssueDataclass(
        title=issue["title"],
        number=issue["number"],
        body=issue["body"],
        is_closed=issue["state"] == "closed",
        closed_at=issue["closed_at"],
        state_reason=issue["state_reason"],
        is_locked=issue["locked"],
        lock_reason=issue["active_lock_reason"],
        repository=repository,
        created_at=issue["created_at"],
        updated_at=issue["updated_at"],
    )


def transform_comments(comment: dict, issue_number: int) -> CommentsDataclass:
    """Transforms a GitHub comment to a dictionary with the required fields.

    Args:
        comment (dict): The GitHub comment to transform.
        issue_number (int): The issue number where the comment belongs.

    Returns:
        IssueCommentBodyDataclass: The transformed GitHub comment.
    """

    issue = get_object_or_404(Issue, number=issue_number)

    return CommentsDataclass(
        comment_id=comment["id"],
        body=comment["body"],
        issue=issue,
        created_at=comment["created_at"],
        updated_at=comment["updated_at"],
    )
