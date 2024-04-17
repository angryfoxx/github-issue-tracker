import pytest
from rest_framework import exceptions, status

from gissues.extensions.github_client.client import GitHubResponse, ServiceUnavailable


def test_GitHubResponse_exception_handler_500_error():
    response = GitHubResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal Server Error"},
        is_ok=False,
    )

    with pytest.raises(ServiceUnavailable) as exc_info:
        response.exception_handler()

    assert exc_info.value.detail == "Internal Server Error"


def test_GitHubResponse_exception_handler_404_error():
    response = GitHubResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Not Found"},
        is_ok=False,
    )

    with pytest.raises(exceptions.NotFound):
        response.exception_handler()


def test_GitHubResponse_exception_handler_400_error():
    response = GitHubResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Bad Request"},
        is_ok=False,
    )

    with pytest.raises(exceptions.ValidationError) as exc_info:
        response.exception_handler()

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["message"].code == 1000


def test_GitHubResponse_exception_handler_ok_response():
    response = GitHubResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "OK"},
        is_ok=True,
    )

    with pytest.raises(AssertionError):
        response.exception_handler()


def test_ServiceUnavailable_exception():
    exception = ServiceUnavailable()
    assert exception.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert exception.default_code == "service_unavailable"
    assert exception.default_detail == (
        "GitHub API is currently unavailable. Please try again later."
        "If the problem persists, please contact the system administrator."
    )
