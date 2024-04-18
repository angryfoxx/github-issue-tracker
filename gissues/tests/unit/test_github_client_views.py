from unittest.mock import Mock

from rest_framework import serializers

import pytest

from gissues.extensions.github_client.client import GitHubResponse
from gissues.extensions.github_client.views import GitHubClientViewSet


class DummySerializer(serializers.Serializer):
    pass


class DummyActionSerializer(serializers.Serializer):
    pass


@pytest.mark.parametrize(
    "action, expected_serializer",
    [
        ("list", DummySerializer),
        ("retrieve", DummyActionSerializer),
    ],
)
def test_get_serializer_class(action, expected_serializer):
    class TestGitHubClientViewSet(GitHubClientViewSet):
        serializer_classes = {
            "list": DummySerializer,
            "retrieve": DummyActionSerializer,
        }

    view = TestGitHubClientViewSet()
    view.action = action

    serializer = view.get_serializer_class()

    assert serializer == expected_serializer


def test_get_serializer_class_raises_assertion_error():
    view = GitHubClientViewSet()
    view.action = "create"

    with pytest.raises(AssertionError):
        view.get_serializer_class()


def test_get_object_from_github():
    mock_response = Mock(spec=GitHubResponse, is_ok=True, content={"key": "value"}, status_code=200)
    mock_func = Mock(return_value=mock_response)

    obj = GitHubClientViewSet.get_object_from_github(mock_func, key="value")

    assert obj == {"key": "value"}

    mock_func.assert_called_once_with(key="value")


def test_get_object_from_github_raises_exception():
    mock_response = Mock(spec=GitHubResponse, is_ok=False, content={"message": "Not Found"}, status_code=404)
    mock_response.exception_handler = Mock(side_effect=Exception("Not Found"))
    mock_func = Mock(return_value=mock_response)

    with pytest.raises(Exception) as exc_info:
        GitHubClientViewSet.get_object_from_github(mock_func, key="value")

    assert str(exc_info.value) == "Not Found"

    mock_func.assert_called_once_with(key="value")
