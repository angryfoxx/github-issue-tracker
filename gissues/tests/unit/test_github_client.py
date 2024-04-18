from unittest.mock import Mock, call, patch

from rest_framework import exceptions, status

import pytest
from requests.exceptions import ConnectionError, Timeout

from gissues.extensions.github_client.client import (
    GitHubClient,
    GitHubComments,
    GitHubIssues,
    GitHubRepositories,
    GitHubResponse,
    ServiceUnavailable,
)


@pytest.mark.parametrize(
    "status_code, content, is_ok",
    [
        (200, {"key": "value"}, True),
        (404, {"message": "Not Found"}, False),
        (500, {"message": "Internal Server Error"}, False),
    ],
)
def test_GitHubResponse(status_code, content, is_ok):
    response = GitHubResponse(status_code, content, is_ok)

    assert response.status_code == status_code
    assert response.content == content
    assert response.is_ok == is_ok


@pytest.mark.parametrize(
    "status_code, content, is_ok, expected_exception",
    [
        (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"message": "Internal Server Error"},
            False,
            ServiceUnavailable,
        ),
        (
            status.HTTP_404_NOT_FOUND,
            {"message": "Not Found"},
            False,
            exceptions.NotFound,
        ),
        (
            status.HTTP_400_BAD_REQUEST,
            {"message": "Bad Request"},
            False,
            exceptions.ValidationError,
        ),
        (status.HTTP_200_OK, {"message": "OK"}, True, AssertionError),
    ],
)
def test_GitHubResponse_exception_handler(status_code, content, is_ok, expected_exception):
    response = GitHubResponse(status_code, content, is_ok)

    with pytest.raises(expected_exception) as exc_info:
        response.exception_handler()

    if expected_exception == ServiceUnavailable:
        assert exc_info.value.detail == content["message"]

    elif expected_exception == exceptions.ValidationError:
        assert exc_info.value.detail["message"].code == "1000"
        assert exc_info.value.detail == content


def test_ServiceUnavailable_exception():
    exception = ServiceUnavailable()
    assert exception.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert exception.default_code == "service_unavailable"
    assert exception.default_detail == (
        "GitHub API is currently unavailable. Please try again later."
        "If the problem persists, please contact the system administrator."
    )


@patch("gissues.extensions.github_client.client.requests.Session")
def test_GitHubClient_session_without_token(mock_session):
    mock_session.return_value.headers = {}

    client = GitHubClient()
    session = client.session

    assert session.headers == {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    mock_session.assert_called_once()


@patch("gissues.extensions.github_client.client.requests.Session")
def test_GitHubClient_session_with_token(mock_session):
    mock_session.return_value.headers = {}

    client = GitHubClient()
    client.client_token = "secret_token"
    session = client.session

    assert session.headers == {
        "Authorization": "Bearer secret_token",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    mock_session.assert_called_once()


@pytest.mark.parametrize(
    "data, expected_data",
    [
        (None, None),
        ({"dict": "value"}, {"dict": "value"}),
        (
            {"dict": "value", "token": "secret_token"},
            {"dict": "value", "token": "********"},
        ),
        (
            {"dict": "value", "ToKeN": "secret_token"},
            {"dict": "value", "ToKeN": "********"},
        ),
    ],
)
def test_GitHubClient_mask_secret_info(data, expected_data):
    client = GitHubClient()
    assert client._mask_secret_info(data) == expected_data


@patch("gissues.extensions.github_client.client.GitHubClient._mask_secret_info")
def test_GitHubClient_log_request(mock_mask_secret_info, caplog):
    mock_mask_secret_info.side_effect = lambda x: x

    client = GitHubClient()
    with caplog.at_level("INFO"):
        client._log_request(
            "GET",
            "https://www.test.com/test-endpoint",
            {"key": "value"},
            {"data": "value"},
            {"response": "value"},
            200,
        )

    assert mock_mask_secret_info.call_args_list == [
        call({"key": "value"}),
        call({"data": "value"}),
    ]

    assert (
        "Request Method: GET\n"
        "Request URL: https://www.test.com/test-endpoint\n"
        "Request Headers: {'key': 'value'}\n"
        "Request Body: {'data': 'value'}\n"
        "Response Body: {'response': 'value'}\n"
        "Response Status Code: 200\n"
    ) in caplog.text


@patch("gissues.extensions.github_client.client.GitHubClient.session")
@pytest.mark.parametrize(
    "mock_session_side_effect, expected_exception",
    [
        (Timeout, ServiceUnavailable),
        (ConnectionError, ServiceUnavailable),
    ],
)
def test_GitHubClient_make_request_non_succeed_ones(mock_session, mock_session_side_effect, expected_exception):
    mock_session.request.side_effect = mock_session_side_effect

    client = GitHubClient()
    with pytest.raises(expected_exception):
        client.make_request("GET", "/test-endpoint")


@patch("gissues.extensions.github_client.client.GitHubClient.session")
@patch(
    "gissues.extensions.github_client.client.GitHubClient._log_request",
    return_value=None,
)
@patch(
    "gissues.extensions.github_client.client.GitHubResponse",
)
@pytest.mark.parametrize(
    "status_code, content, is_ok",
    [
        (200, {"key": "value"}, True),
        (404, {"message": "Not Found"}, False),
        (500, {"message": "Internal Server Error"}, False),
    ],
)
def test_GitHubClient_make_request_success(
    mock_github_response, mock_log_request, mock_session, status_code, content, is_ok
):
    mock_response = Mock()
    mock_response.request.body = None
    mock_response.status_code = status_code
    mock_response.json.return_value = content
    mock_response.ok = is_ok

    mock_session.request.return_value = mock_response
    mock_session.headers = {}

    mock_github_response.return_value = Mock(spec=GitHubResponse, status_code=status_code, content=content, is_ok=is_ok)

    client = GitHubClient()
    response = client.make_request("GET", "/test-endpoint")

    assert response.status_code == status_code
    assert response.content == content
    assert response.is_ok == is_ok

    mock_github_response.assert_called_once_with(status_code=status_code, content=content, is_ok=is_ok)
    mock_session.request.assert_called_once_with("GET", "https://www.test.com/test-endpoint")
    mock_log_request.assert_called_once_with(
        "GET",
        "https://www.test.com/test-endpoint",
        {},
        None,
        content,
        status_code,
    )


@patch("gissues.extensions.github_client.client.GitHubIssues")
def test_GitHubClient_issues_property(mock_github_issues):
    client = GitHubClient()
    assert client.issues == mock_github_issues.return_value

    mock_github_issues.assert_called_once_with(client)


@patch("gissues.extensions.github_client.client.GitHubRepositories")
def test_GitHubClient_repositories_property(mock_github_repositories):
    client = GitHubClient()
    assert client.repositories == mock_github_repositories.return_value

    mock_github_repositories.assert_called_once_with(client)


@patch("gissues.extensions.github_client.client.GitHubComments")
def test_GitHubClient_comments_property(mock_github_comments):
    client = GitHubClient()
    assert client.comments == mock_github_comments.return_value

    mock_github_comments.assert_called_once_with(client)


def test_GitHubIssues_list(mocked_github_client):
    client = GitHubIssues(mocked_github_client)
    response = client.list("owner", "repo")

    assert response.status_code == 200
    assert response.content == {"dummy": "data"}
    assert response.is_ok is True

    mocked_github_client.make_request.assert_called_once_with("GET", "/repos/owner/repo/issues?state=all")


def test_GitHubIssues_detail(mocked_github_client):
    client = GitHubIssues(mocked_github_client)
    response = client.detail("owner", "repo", 1)

    assert response.status_code == 200
    assert response.content == {"dummy": "data"}
    assert response.is_ok is True

    mocked_github_client.make_request.assert_called_once_with("GET", "/repos/owner/repo/issues/1")


def test_GitHubRepositories_list(mocked_github_client):
    client = GitHubRepositories(mocked_github_client)
    response = client.list("username")

    assert response.status_code == 200
    assert response.content == {"dummy": "data"}
    assert response.is_ok is True

    mocked_github_client.make_request.assert_called_once_with("GET", "/users/username/repos")


def test_GitHubRepositories_detail(mocked_github_client):
    client = GitHubRepositories(mocked_github_client)
    response = client.detail("owner", "repo")

    assert response.status_code == 200
    assert response.content == {"dummy": "data"}
    assert response.is_ok is True

    mocked_github_client.make_request.assert_called_once_with("GET", "/repos/owner/repo")


def test_GitHubComments_list(mocked_github_client):
    client = GitHubComments(mocked_github_client)
    response = client.list("owner", "repo", 1)

    assert response.status_code == 200
    assert response.content == {"dummy": "data"}
    assert response.is_ok is True

    mocked_github_client.make_request.assert_called_once_with("GET", "/repos/owner/repo/issues/1/comments")


def test_GitHubComments_detail(mocked_github_client):
    client = GitHubComments(mocked_github_client)
    response = client.detail("owner", "repo", 1)

    assert response.status_code == 200
    assert response.content == {"dummy": "data"}
    assert response.is_ok is True

    mocked_github_client.make_request.assert_called_once_with("GET", "/repos/owner/repo/issues/comments/1")
