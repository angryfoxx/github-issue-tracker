from unittest.mock import Mock

from rest_framework.test import APIClient

import pytest
from pytest_factoryboy import register

from gissues.extensions.github_client.client import GitHubClient, GitHubResponse
from gissues.extensions.utils import APIRootView
from gissues.tests.factories import (
    CommentsFactory,
    IssueFactory,
    RepositoryFactory,
    UserFactory,
    UserRepositoryFollowFactory,
)


@pytest.fixture
def mocked_github_client():
    mock_github_client = Mock(spec=GitHubClient)
    mock_github_client.make_request.return_value = Mock(
        spec=GitHubResponse, status_code=200, content={"dummy": "data"}, is_ok=True
    )

    return mock_github_client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_root_view():
    return APIRootView()


register(RepositoryFactory)
register(IssueFactory)
register(CommentsFactory)
register(UserFactory)
register(UserRepositoryFollowFactory)
