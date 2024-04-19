from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet

from rest_framework import mixins, permissions
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import GenericViewSet

from gissues.extensions.auth.models import UserRepositoryFollow
from gissues.extensions.github.api.serializers import RepositorySerializer
from gissues.extensions.github.models import Repository
from gissues.extensions.utils import pagination_factory


class UserRepositoryFollowViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = UserRepositoryFollow.objects.all()
    serializer_class = RepositorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = pagination_factory(page_size=10)
    filter_backends = [OrderingFilter]
    ordering = ["id"]
    http_method_names = ["head", "options", "get"]

    def get_queryset(self) -> QuerySet[Repository]:
        request_user: AbstractBaseUser = self.request.user
        return Repository.objects.filter(
            followers__user=request_user,
        )
