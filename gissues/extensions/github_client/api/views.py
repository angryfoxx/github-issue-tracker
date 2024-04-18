from typing import Any

from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from gissues.extensions.github_client.client import GitHubResponse
from gissues.extensions.utils import pagination_factory


class GitHubClientViewSet(ReadOnlyModelViewSet):
    serializer_classes: dict[str, type[serializers.BaseSerializer[Any]]] = {}
    pagination_class = pagination_factory(page_size=10)
    filter_backends = [OrderingFilter]

    def get_serializer_class(self):
        serializer = self.serializer_classes.get(self.action, self.serializer_class)
        assert serializer is not None
        return serializer

    @staticmethod
    def get_object_from_github(func: callable, **kwargs):
        obj: GitHubResponse = func(**kwargs)
        if not obj.is_ok:
            raise obj.exception_handler()

        return obj.content
