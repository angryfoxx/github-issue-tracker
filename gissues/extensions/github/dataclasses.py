from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from gissues.extensions.github.models import Issue


@dataclass
class RepositoryDataclass:
    name: str
    owner_name: str
    description: str
    is_private: bool
    is_fork: bool
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime


@dataclass
class IssueDataclass:
    title: str
    number: int
    is_closed: bool
    closed_at: datetime
    state_reason: Issue.StateReason
    is_locked: bool
    lock_reason: Issue.LockReason
    repository: Optional[RepositoryDataclass]
    created_at: datetime
    updated_at: datetime


@dataclass
class CommentsDataclass:
    comment_id: int
    issue: IssueDataclass
    created_at: datetime
    updated_at: datetime


@dataclass
class IssueCommentBodyDataclass:
    body: str
    issue: Optional[IssueDataclass]
    comment: Optional[CommentsDataclass]
