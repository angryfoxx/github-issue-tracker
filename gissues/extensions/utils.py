from typing import Any, Optional, cast

from django import urls
from django.urls import URLPattern, URLResolver

from rest_framework.pagination import CursorPagination, LimitOffsetPagination, PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import APIRootView as BaseAPIRootView


def pagination_factory(
    base: Optional[type[PageNumberPagination] | type[CursorPagination] | type[LimitOffsetPagination]] = None,
    **kwargs: Any,
) -> type:
    """Creates a pagination class.

    Creates a pagination class that inherits from the given base class and
    has the given attributes.

    The attributes that can be added are:
        - page_size_query_param: The query parameter to use for the page size.
        - max_page_size: The maximum page size.
        - page_query_param: The query parameter to use for the page number.

    These can be set via the API as query parameters (e.g. ?page=1&page_size=10).

    Args:
        base (PageNumberPagination, CursorPagination, LimitOffsetPagination): The base pagination class.
            Defaults to None.
        **kwargs: The attributes to add to the pagination class.

    Returns:
        type: The pagination class.

    Usage:
    >>> from gissues.extensions.utils import pagination_factory
    >>> # Basic Usage:
    >>> class MyView(generics.ListAPIView):
    ...     pagination_class = pagination_factory(page_size=10)
    """
    base = base or PageNumberPagination
    kwargs.setdefault("page_size_query_param", "page_size")
    kwargs.setdefault("max_page_size", 99_999)
    kwargs.setdefault("page_query_param", "page")
    return type("FactoryPagination", (base,), kwargs)


class APIRootView(BaseAPIRootView):
    # Inspired by https://github.com/realsuayip/asu/blob/03ce9f4a6b8f4a0f153055c00d5689d14f6bdfe0/asu/views.py#L35
    def resolve_url(self, namespace: str, url: URLPattern) -> str | None:
        try:
            relpath = reverse(
                namespace + ":" + str(url.name),
                kwargs=dict(url.pattern.regex.groupindex),
                request=self.request,
            )
        except urls.NoReverseMatch:
            return None
        return self.request.build_absolute_uri(relpath)

    def get_routes(self) -> dict[str, tuple[str, str]]:
        url_resolver = urls.get_resolver(urls.get_urlconf())
        resolvers = url_resolver.url_patterns

        filtered_resolvers = filter(
            lambda resolver: isinstance(resolver, URLResolver) and resolver.namespace == "api", resolvers
        )

        return self.visit(next(filtered_resolvers))

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response(self.get_routes())

    @staticmethod
    def convert_pattern_to_human_readable(pattern: str) -> str:
        return (
            pattern.replace("(?P<", "{")
            .replace(">[^/.]+)", "}")
            .replace(">\\w+", "}")
            .replace("^", "")
            .replace("$", "")
            .rstrip("/")
        )

    def visit(self, resolver: URLResolver) -> dict[str, tuple[str, str]]:
        values = {}
        for entry in resolver.url_patterns:
            if isinstance(entry, URLResolver):
                values.update(self.visit(entry))
            else:
                entry_name: str = entry.name
                if entry_name == "api-root":
                    continue

                values[entry_name] = (
                    self.convert_pattern_to_human_readable(str(entry.pattern)),
                    cast(str, self.resolve_url("api", entry)),
                )
        return values
