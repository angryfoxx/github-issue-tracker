from typing import Optional

from gissues.extensions.github.dataclasses import (
    CommentsDataclass,
    IssueCommentBodyDataclass,
    IssueDataclass,
    RepositoryDataclass,
)


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


def transform_issue(issue: dict, repository: Optional[RepositoryDataclass] = None) -> IssueDataclass:
    """Transforms a GitHub issue to a dictionary with the required fields.

    Args:
        issue (dict): The GitHub issue to transform.
        repository (Optional[RepositoryDataclass], optional): The repository where the issue belongs. Defaults to None.

    Returns:
        IssueDataclass: The transformed GitHub issue.
    """
    return IssueDataclass(
        title=issue["title"],
        number=issue["number"],
        is_closed=issue["state"] == "closed",
        closed_at=issue["closed_at"],
        state_reason=issue["state_reason"],
        is_locked=issue["locked"],
        lock_reason=issue["active_lock_reason"],
        repository=repository,
        created_at=issue["created_at"],
        updated_at=issue["updated_at"],
    )


def transform_comments(comment: dict, issue: Optional[IssueDataclass] = None) -> IssueCommentBodyDataclass:
    """Transforms a GitHub comment to a dictionary with the required fields.

    Args:
        comment (dict): The GitHub comment to transform.
        issue (Optional[IssueDataclass], optional): The issue where the comment belongs. Defaults to None.

    Returns:
        IssueCommentBodyDataclass: The transformed GitHub comment.
    """
    return IssueCommentBodyDataclass(
        body=comment["body"],
        issue=issue,
        comment=CommentsDataclass(
            comment_id=comment["id"],
            issue=issue,
            created_at=comment["created_at"],
            updated_at=comment["updated_at"],
        ),
    )
