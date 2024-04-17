import logging
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings
from rest_framework import exceptions, serializers, status

logger = logging.getLogger(__name__)


class ServiceUnavailable(exceptions.APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = "service_unavailable"
    default_detail = (
        "GitHub API is currently unavailable. Please try again later."
        "If the problem persists, please contact the system administrator."
    )


@dataclass
class GitHubResponse:
    status_code: int
    content: dict
    is_ok: bool

    def exception_handler(self):
        assert not self.is_ok

        if self.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise ServiceUnavailable(self.content.get("message"))

        if self.status_code == status.HTTP_404_NOT_FOUND:
            raise exceptions.NotFound("Resource not found.")

        raise serializers.ValidationError(self.content, code=1000)


class GitHubClient:
    client_url = settings.GITHUB_CLIENT_URL
    client_token = settings.GITHUB_CLIENT_AUTH_TOKEN

    @property
    def session(self):
        session = requests.Session()
        session.headers.update(
            {
                "Authorization": f"Bearer {self.client_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        return session

    @staticmethod
    def _mask_secret_info(data: Optional[dict] = None) -> Optional[dict]:
        """Mask secret information in the data.

        Args:
            data (Optional[dict]): The data to mask.

        Returns:
            dict | None: The masked data.

        """
        if not data:
            return None

        secret_keys = {"token", "password", "secret", "authorization", "key"}

        for key, value in data.items():
            if key.lower() in secret_keys:
                data[key] = "********"

        return data

    def _log_request(
        self,
        method,
        url,
        headers,
        request_body,
        response_body,
        response_status,
    ):
        logger.info(
            "Request Method: %s\n"
            "Request URL: %s\n"
            "Request Headers: %s\n"
            "Request Body: %s\n"
            "Response Body: %s\n"
            "Response Status Code: %s\n",
            method,
            url,
            self._mask_secret_info(headers),
            self._mask_secret_info(request_body),
            response_body,
            response_status,
        )

    def make_request(self, method: str, endpoint: str, **kwargs) -> GitHubResponse:
        """Make a request to the GitHub API.

        Args:
            method (str): The HTTP method to use.
            endpoint (str): The URL to request.
            **kwargs: Additional keyword arguments to pass to `requests.Session.request`.

        Returns:
            GitHubResponse: The response from the GitHub API.

        """
        url = self.client_url + endpoint
        try:
            response = self.session.request(method, url, **kwargs)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise ServiceUnavailable()

        github_response = GitHubResponse(
            status_code=response.status_code,
            content=response.json(),
            is_ok=response.ok,
        )

        self._log_request(
            method,
            url,
            self.session.headers,
            response.request.body,
            github_response.content,
            github_response.status_code,
        )
        return github_response

    @property
    def issues(self) -> "GitHubIssues":
        """Get the GitHub issues client."""
        return GitHubIssues(self)

    @property
    def repositories(self) -> "GitHubRepositories":
        """Get the GitHub repositories client."""
        return GitHubRepositories(self)


class GitHubIssues:
    _path_list = "/repos/%(owner)s/%(repo)s/issues"
    _path_detail = "/repos/%(owner)s/%(repo)s/issues/%(issue_number)s"

    def __init__(self, base_client: GitHubClient):
        self.base_client = base_client

    def list(self, owner: str, repo: str) -> GitHubResponse:
        """List issues for a repository.

        Args:
            owner (str): The repository owner.
            repo (str): The repository name.

        Returns:
            GitHubResponse: The response from the GitHub API.

        """
        url = self._path_list % {"owner": owner, "repo": repo}
        return self.base_client.make_request("GET", url)

    def detail(self, owner: str, repo: str, issue_number: int | str) -> GitHubResponse:
        """Get details for an issue.

        Args:
            owner (str): The repository owner.
            repo (str): The repository name.
            issue_number (int | str): The issue number.

        Returns:
            GitHubResponse: The response from the GitHub API.

        """
        url = self._path_detail % {
            "owner": owner,
            "repo": repo,
            "issue_number": issue_number,
        }
        return self.base_client.make_request("GET", url)


class GitHubRepositories:
    _path_list = "/users/%(username)s/repos"
    _path_detail = "/repos/%(owner)s/%(repo)s"

    def __init__(self, base_client: GitHubClient):
        self.base_client = base_client

    def list(self, username: str) -> GitHubResponse:
        """List repositories for a user.

        Args:
            username (str): The user's username.

        Returns:
            GitHubResponse: The response from the GitHub API.

        """
        url = self._path_list % {"username": username}
        return self.base_client.make_request("GET", url)

    def detail(self, owner: str, repo: str) -> GitHubResponse:
        """Get details for a repository.

        Args:
            owner (str): The repository owner.
            repo (str): The repository name.

        Returns:
            GitHubResponse: The response from the GitHub API.

        """
        url = self._path_detail % {"owner": owner, "repo": repo}
        return self.base_client.make_request("GET", url)


github_client = GitHubClient()
