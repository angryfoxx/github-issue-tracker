from django.db.models import OuterRef, QuerySet, Subquery

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from gissues.extensions.auth.models import UserRepositoryFollow
from gissues.extensions.github.api.serializers import CommentsSerializer, IssueSerializer, RepositorySerializer
from gissues.extensions.github.models import Comments, Issue, IssueCommentBody, Repository
from gissues.extensions.github.transformers import transform_comments, transform_issue, transform_repository
from gissues.extensions.github_client.api.views import GitHubClientViewSet
from gissues.extensions.github_client.client import github_client


class RepositoryViewSet(GitHubClientViewSet):
    serializer_class = RepositorySerializer
    queryset = Repository.objects.all()
    lookup_field = "name"
    lookup_url_kwarg = "repository_name"
    ordering = ["name"]

    def get_queryset(self) -> QuerySet[Repository]:
        qs = super().get_queryset()
        return qs.filter(owner_name=self.kwargs["repository_owner"])

    def get_object(self) -> Repository:
        qs = self.get_queryset()
        repository_name = self.kwargs[self.lookup_url_kwarg]

        if obj := qs.filter(name=repository_name).first():
            return obj

        obj = self.get_object_from_github(
            github_client.repositories.detail,
            owner=self.kwargs["repository_owner"],
            repository_name=repository_name,
        )

        transformed_data = transform_repository(obj).dict()

        return Repository.objects.create(**transformed_data)

    @action(detail=True, methods=["POST"], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request: Request, repository_owner: str, repository_name: str) -> Response:
        request_user = request.user

        if UserRepositoryFollow.objects.filter(
            user=request_user, repository__name=repository_name, repository__owner_name=repository_owner
        ).exists():
            return Response(status=status.HTTP_200_OK)

        UserRepositoryFollow.objects.create(user=request.user, repository=self.get_object())
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"], permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request: Request, repository_owner: str, repository_name: str) -> Response:
        UserRepositoryFollow.objects.filter(
            user=request.user, repository__name=repository_name, repository__owner_name=repository_owner
        ).delete()
        return Response(status=status.HTTP_200_OK)


class IssueViewSet(GitHubClientViewSet):
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()
    lookup_field = "number"
    lookup_url_kwarg = "issue_number"
    ordering = ["number"]

    def get_queryset(self) -> QuerySet[Issue]:
        qs = super().get_queryset()
        repository = get_object_or_404(
            Repository, name=self.kwargs["repository_repository_name"], owner_name=self.kwargs["repository_owner"]
        )

        qs = qs.annotate(body_text=Subquery(IssueCommentBody.objects.filter(issue=OuterRef("pk")).values("body")[:1]))

        return qs.filter(repository=repository)

    def get_object(self) -> Issue:
        queryset = self.get_queryset()
        issue_number = self.kwargs[self.lookup_url_kwarg]

        if obj := queryset.filter(number=issue_number).first():
            return obj

        obj = self.get_object_from_github(
            github_client.issues.detail,
            owner=self.kwargs["repository_owner"],
            repository_name=self.kwargs["repository_repository_name"],
            issue_number=issue_number,
        )

        transformed_data = transform_issue(
            obj, self.kwargs["repository_repository_name"], self.kwargs["repository_owner"]
        ).dict()
        body_text = transformed_data.pop("body", None)

        issue = Issue.objects.create(**transformed_data)

        if body_text:
            IssueCommentBody.objects.create(issue=issue, body=body_text)

        return self.get_queryset().get(pk=issue.pk)


class CommentsViewSet(GitHubClientViewSet):
    serializer_class = CommentsSerializer
    queryset = Comments.objects.all()
    lookup_field = "comment_id"
    lookup_url_kwarg = "comment_id"
    ordering = ["created_at"]

    def get_queryset(self) -> QuerySet[Comments]:
        qs = super().get_queryset()
        issue = get_object_or_404(Issue, number=self.kwargs["issue_issue_number"])

        qs = qs.annotate(body_text=Subquery(IssueCommentBody.objects.filter(comment=OuterRef("pk")).values("body")[:1]))

        return qs.filter(issue=issue)

    def get_object(self) -> Comments:
        queryset = self.get_queryset()
        comment_id = self.kwargs[self.lookup_url_kwarg]

        if obj := queryset.filter(comment_id=comment_id).first():
            return obj

        obj = self.get_object_from_github(
            github_client.comments.detail,
            owner=self.kwargs["repository_owner"],
            repository_name=self.kwargs["repository_repository_name"],
            comment_id=comment_id,
        )

        transformed_data = transform_comments(obj, self.kwargs["issue_issue_number"]).dict()
        body_text = transformed_data.pop("body", None)

        comment = Comments.objects.create(**transformed_data)

        if body_text:
            IssueCommentBody.objects.create(issue=comment.issue, comment=comment, body=body_text)

        return self.get_queryset().get(pk=comment.pk)
