from dataclasses import asdict, dataclass
from datetime import datetime

from gissues.extensions.github.models import Issue, Repository


@dataclass
class BaseDataclass:
    def dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class RepositoryDataclass(BaseDataclass):
    name: str
    owner_name: str
    description: str
    is_private: bool
    is_fork: bool
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime


@dataclass
class IssueDataclass(BaseDataclass):
    title: str
    number: int
    body: str
    is_closed: bool
    closed_at: datetime
    state_reason: Issue.StateReason
    is_locked: bool
    lock_reason: Issue.LockReason
    repository: RepositoryDataclass | Repository
    created_at: datetime
    updated_at: datetime


@dataclass
class CommentsDataclass(BaseDataclass):
    comment_id: int
    body: str
    issue: IssueDataclass | Issue
    created_at: datetime
    updated_at: datetime
