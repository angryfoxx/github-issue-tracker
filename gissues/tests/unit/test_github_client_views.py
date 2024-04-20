from unittest.mock import Mock

from rest_framework import serializers

import pytest

from gissues.extensions.github_client.api.views import GitHubClientViewSet
from gissues.extensions.github_client.client import GitHubResponse


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

    viewset = GitHubClientViewSet()
    viewset.client_detail_function = mock_func

    obj = viewset.get_object_from_github(key="value")

    assert obj == {"key": "value"}

    mock_func.assert_called_once_with(key="value")


def test_get_object_from_github_raises_exception():
    mock_response = Mock(spec=GitHubResponse, is_ok=False, content={"message": "Not Found"}, status_code=404)
    mock_response.exception_handler = Mock(side_effect=Exception("Not Found"))
    mock_func = Mock(return_value=mock_response)

    viewset = GitHubClientViewSet()
    viewset.client_detail_function = mock_func

    with pytest.raises(Exception) as exc_info:
        viewset.get_object_from_github(key="value")

    assert str(exc_info.value) == "Not Found"

    mock_func.assert_called_once_with(key="value")


def test_get_object_or_sync_existing_object():
    mock_qs = Mock()
    mock_qs.filter.return_value.first.return_value = "existing_object"

    viewset = GitHubClientViewSet()
    viewset.get_queryset = Mock(return_value=mock_qs)
    viewset.kwargs = {"number": 1}
    viewset.lookup_field = "number"

    obj = viewset.get_object_or_sync({"number": 1})

    assert obj == "existing_object"

    mock_qs.filter.assert_called_once_with(number=1)
    mock_qs.filter.return_value.first.assert_called_once()


def test_get_object_or_sync_new_object():
    mock_qs = Mock()
    mock_qs.filter.return_value.first.return_value = None

    mock_response = Mock(spec=GitHubResponse, is_ok=True, content={"key": "value"}, status_code=200)
    mock_func = Mock(return_value=mock_response)

    viewset = GitHubClientViewSet()
    viewset.get_queryset = Mock(return_value=mock_qs)
    viewset.client_detail_function = mock_func
    viewset.model = Mock()
    transform_function = Mock()
    transform_function.return_value.dict.return_value = {"key": "value"}
    viewset.transform_function = transform_function
    viewset.kwargs = {"number": 1}
    viewset.lookup_field = "number"

    obj = viewset.get_object_or_sync({"number": 1})

    assert obj == viewset.model.objects.create.return_value

    mock_qs.filter.assert_called_once_with(number=1)
    mock_qs.filter.return_value.first.assert_called_once()
    mock_func.assert_called_once_with(number=1)
    viewset.transform_function.assert_called_once_with({"key": "value"})
    viewset.model.objects.create.assert_called_once_with(key="value")


def test_get_object_or_sync_invalid_lookup_value():
    mock_qs = Mock()
    mock_qs.filter.side_effect = ValueError

    viewset = GitHubClientViewSet()
    viewset.get_queryset = Mock(return_value=mock_qs)
    viewset.kwargs = {"number": "invalid"}
    viewset.lookup_field = "number"

    with pytest.raises(serializers.ValidationError) as exc_info:
        viewset.get_object_or_sync({"number": "invalid"})

    assert (
        exc_info.value.args[0]
        == "Invalid value 'invalid' for number. This field must be a valid type. Please check the URL and try again. If the problem persists, please contact the system administrator or check the API documentation."
    )

    mock_qs.filter.assert_called_once_with(number="invalid")
