from unittest.mock import Mock

import pytest
from pytest_factoryboy import register

from gissues.tests.factories import (
    CommentsFactory,
    IssueCommentBodyFactory,
    IssueFactory,
    RepositoryFactory,
)


@pytest.fixture
def mocked_github_client():
    from gissues.extensions.github_client.client import GitHubClient, GitHubResponse

    mock_github_client = Mock(spec=GitHubClient)
    mock_github_client.make_request.return_value = Mock(
        spec=GitHubResponse, status_code=200, content={"dummy": "data"}, is_ok=True
    )

    return mock_github_client


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


register(RepositoryFactory)
register(IssueFactory)
register(CommentsFactory)
register(IssueCommentBodyFactory)
