from unittest.mock import Mock, patch

from django.http import HttpRequest
from django.urls import NoReverseMatch
from django.urls.resolvers import URLPattern, URLResolver

import pytest


@patch("gissues.extensions.utils.reverse")
def test_resolve_url(mock_reverse, api_root_view):
    mock_request = Mock(spec=HttpRequest)
    mock_request.build_absolute_uri = Mock(return_value="http://test.com")
    api_root_view.request = mock_request

    url_pattern = Mock(
        spec=URLPattern,
        pattern=Mock(regex=Mock(groupindex={"name": 1})),
    )
    url_pattern.name = "test-pattern"
    mock_reverse.return_value = "api:test-pattern"

    resolved_url = api_root_view.resolve_url("api", url_pattern)

    assert resolved_url == "http://test.com"

    mock_reverse.assert_called_once_with("api:test-pattern", kwargs={"name": 1}, request=mock_request)

    api_root_view.request.build_absolute_uri.assert_called_once_with("api:test-pattern")


@patch("gissues.extensions.utils.reverse")
def test_resolve_url_no_reverse(mock_reverse, api_root_view):
    mock_request = Mock(spec=HttpRequest)
    api_root_view.request = mock_request

    url_pattern = Mock(
        spec=URLPattern,
        pattern=Mock(regex=Mock(groupindex={"name": 1})),
    )
    url_pattern.name = "test-pattern"
    mock_reverse.side_effect = NoReverseMatch

    resolved_url = api_root_view.resolve_url("api", url_pattern)

    assert resolved_url is None

    mock_reverse.assert_called_once_with("api:test-pattern", kwargs={"name": 1}, request=mock_request)

    api_root_view.request.build_absolute_uri.assert_not_called()


@patch("gissues.extensions.utils.urls")
@patch("gissues.extensions.utils.APIRootView.visit")
def test_get_routes(mock_visit, mock_urls, api_root_view):
    mock_get_urlconf = Mock()
    mock_url_resolver = Mock()
    mock_url_resolver.url_patterns = [
        Mock(spec=URLResolver, namespace="api", url_patterns=[Mock(spec=URLPattern, name="test-pattern")]),
        Mock(spec=URLResolver, namespace="test", url_patterns=[Mock(spec=URLPattern, name="test-pattern")]),
    ]
    mock_urls.get_resolver.return_value = mock_url_resolver
    mock_urls.get_urlconf.return_value = mock_get_urlconf

    mock_visit.return_value = {"test-pattern": ("test", "http://test.com")}

    routes = api_root_view.get_routes()

    assert routes == {"test-pattern": ("test", "http://test.com")}

    mock_urls.get_resolver.assert_called_once_with(mock_get_urlconf)
    mock_urls.get_urlconf.assert_called_once()
    mock_visit.assert_called_once_with(mock_url_resolver.url_patterns[0])


def test_get_routes_no_patterns(api_root_view):
    mock_url_resolver = Mock()
    mock_url_resolver.url_patterns = []
    mock_url_resolver.namespace = "api"
    with patch("gissues.extensions.utils.urls") as mock_urls:
        mock_urls.get_resolver.return_value = mock_url_resolver
        routes = api_root_view.get_routes()
        assert routes == {}


@pytest.mark.parametrize(
    "pattern, expected",
    [
        ("(?P<name>[^/.]+)/", "{name}"),
        ("(?P<name>\\w+)/", "{name}"),
        ("^", ""),
        ("$", ""),
        ("(?P<name>[^/.]+)/(?P<id>\\w+)/", "{name}/{id}"),
    ],
)
def test_convert_pattern_to_human_readable(pattern, expected, api_root_view):
    assert api_root_view.convert_pattern_to_human_readable(pattern) == expected


def test_visit_resolver_is_none(api_root_view):
    assert api_root_view.visit() == {}


def test_visit_with_api_root_resolver(api_root_view):
    mock_entry = Mock(spec=URLPattern, pattern=Mock())
    mock_entry.name = "api-root"
    resolver = Mock(spec=URLResolver, url_patterns=[mock_entry])

    result = api_root_view.visit(resolver)

    assert result == {}


@patch("gissues.extensions.utils.APIRootView.convert_pattern_to_human_readable")
@patch("gissues.extensions.utils.APIRootView.resolve_url")
def test_visit_with_url_pattern(mock_resolve_url, mock_convert_pattern_to_human_readable, api_root_view):
    mock_entry = Mock(spec=URLPattern, pattern=Mock())
    mock_entry.name = "test-pattern"
    mock_resolve_url.return_value = "http://test.com"
    mock_convert_pattern_to_human_readable.return_value = "test"

    resolver = Mock(spec=URLResolver, url_patterns=[mock_entry])
    resolver.url_patterns = [mock_entry]
    resolver.namespace = "api"

    result = api_root_view.visit(resolver)

    assert result == {"test-pattern": ("test", "http://test.com")}

    mock_resolve_url.assert_called_once_with("api", mock_entry)
    mock_convert_pattern_to_human_readable.assert_called_once_with(str(mock_entry.pattern))


@patch("gissues.extensions.utils.APIRootView.convert_pattern_to_human_readable")
@patch("gissues.extensions.utils.APIRootView.resolve_url")
def test_visit_with_url_resolver(mock_resolve_url, mock_convert_pattern_to_human_readable, api_root_view):
    url_pattern = Mock(spec=URLPattern, pattern=Mock())
    url_pattern.name = "test-pattern2"
    mock_resolver = Mock(spec=URLResolver, url_patterns=[url_pattern])

    mock_resolve_url.return_value = "http://test.com"
    mock_convert_pattern_to_human_readable.return_value = "test"

    resolver = Mock(spec=URLResolver, url_patterns=[mock_resolver])

    result = api_root_view.visit(resolver)

    assert result == {"test-pattern2": ("test", "http://test.com")}

    mock_resolve_url.assert_called_once_with("api", mock_resolver.url_patterns[0])
    mock_convert_pattern_to_human_readable.assert_called_once_with(str(mock_resolver.url_patterns[0].pattern))


@patch("gissues.extensions.utils.APIRootView.get_routes")
def test_api_root_view_get(mock_get_routes, api_root_view):
    mock_get_routes.return_value = {"test": ("test", "http://test.com")}

    response = api_root_view.get(Mock())

    assert response.data == {"test": ("test", "http://test.com")}
