from typing import Any, Callable, Optional, Union

from django.db import models

from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from gissues.extensions.github_client.client import GitHubResponse
from gissues.extensions.utils import pagination_factory


class GitHubClientViewSet(ReadOnlyModelViewSet):
    serializer_classes: dict[str, type[serializers.BaseSerializer[Any]]] = {}
    pagination_class = pagination_factory(page_size=10)
    filter_backends = [OrderingFilter]
    model: models.Model
    transform_function: Callable[[dict[str, Any]], Any]
    client_detail_function: Callable[..., ...]

    def get_serializer_class(self) -> type[serializers.BaseSerializer[Any]]:
        serializer = self.serializer_classes.get(self.action, self.serializer_class)
        assert serializer is not None
        return serializer

    def get_object_from_github(self, **kwargs: Any) -> Union[dict[str, Any], Any]:
        obj: GitHubResponse = self.client_detail_function(**kwargs)
        if not obj.is_ok:
            raise obj.exception_handler()

        return obj.content

    def get_object_or_sync(
        self, github_client_kwargs: dict[str, Any], transform_kwargs: Optional[dict[str, Any]] = None
    ):
        qs = self.get_queryset()

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]

        if obj := qs.filter(**{self.lookup_field: lookup_value}).first():
            return obj

        obj = self.get_object_from_github(
            **github_client_kwargs,
        )

        transform_kwargs = transform_kwargs or {}
        transformed_data = self.transform_function(obj, **transform_kwargs)

        return self.model.objects.create(**transformed_data.dict())
