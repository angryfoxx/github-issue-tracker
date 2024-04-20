from django.db.models import QuerySet

from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from gissues.extensions.auth.models import UserRepositoryFollow
from gissues.extensions.github.api.serializers import CommentsSerializer, IssueSerializer, RepositorySerializer
from gissues.extensions.github.models import Comments, Issue, Repository
from gissues.extensions.github.transformers import transform_comments, transform_issue, transform_repository
from gissues.extensions.github_client.api.views import GitHubClientViewSet
from gissues.extensions.github_client.client import github_client


class RepositoryViewSet(GitHubClientViewSet):
    serializer_class = RepositorySerializer
    queryset = Repository.objects.all()
    model = Repository
    transform_function = staticmethod(transform_repository)
    client_detail_function = github_client.repositories.detail
    lookup_field = "name"
    ordering = ["name"]
    http_method_names = ["head", "options", "get", "post"]

    def get_queryset(self) -> QuerySet[Repository]:
        qs = super().get_queryset()
        return qs.filter(owner_name=self.kwargs["repository_owner"])

    def get_object(self) -> Repository:
        return self.get_object_or_sync(
            {
                "owner_name": self.kwargs["repository_owner"],
                "repository_name": self.kwargs["name"],
            }
        )

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=serializers.Serializer,
    )
    def follow(self, request: Request, repository_owner: str, name: str) -> Response:
        """This action allows a user to follow a repository."""

        request_user = request.user

        if UserRepositoryFollow.objects.filter(
            user=request_user, repository__name=name, repository__owner_name=repository_owner
        ).exists():
            return Response(status=status.HTTP_200_OK)

        UserRepositoryFollow.objects.create(user=request.user, repository=self.get_object())
        return Response(status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=serializers.Serializer,
    )
    def unfollow(self, request: Request, repository_owner: str, name: str) -> Response:
        """This action allows a user to unfollow a repository."""
        UserRepositoryFollow.objects.filter(
            user=request.user, repository__name=name, repository__owner_name=repository_owner
        ).delete()
        return Response(status=status.HTTP_200_OK)


class IssueViewSet(GitHubClientViewSet):
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()
    model = Issue
    transform_function = staticmethod(transform_issue)
    client_detail_function = github_client.issues.detail
    lookup_field = "number"
    ordering = ["number"]

    def get_queryset(self) -> QuerySet[Issue]:
        qs = super().get_queryset()

        repository = Repository.objects.get(
            name=self.kwargs["repository_name"], owner_name=self.kwargs["repository_owner"]
        )
        return qs.filter(repository=repository)

    def get_object(self) -> Issue:
        repository_name = self.kwargs["repository_name"]
        owner_name = self.kwargs["repository_owner"]
        return self.get_object_or_sync(
            {
                "owner_name": owner_name,
                "repository_name": repository_name,
                "issue_number": self.kwargs["number"],
            },
            {"repository_name": repository_name, "owner_name": owner_name},
        )


class CommentsViewSet(GitHubClientViewSet):
    serializer_class = CommentsSerializer
    queryset = Comments.objects.all()
    model = Comments
    transform_function = staticmethod(transform_comments)
    client_detail_function = github_client.comments.detail
    lookup_field = "comment_id"
    ordering = ["created_at"]

    def get_queryset(self) -> QuerySet[Comments]:
        qs = super().get_queryset()
        issue = get_object_or_404(Issue, number=self.kwargs["issue_number"])
        return qs.filter(issue=issue)

    def get_object(self) -> Comments:
        issue_number = self.kwargs["issue_number"]
        return self.get_object_or_sync(
            {
                "owner_name": self.kwargs["repository_owner"],
                "repository_name": self.kwargs["repository_name"],
                "comment_id": self.kwargs["comment_id"],
            },
            {"issue_number": issue_number},
        )
