from typing import Optional, Any

from rest_framework.pagination import CursorPagination, LimitOffsetPagination, PageNumberPagination


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
