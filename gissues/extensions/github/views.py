from django.db.models import OuterRef, Subquery

from rest_framework.generics import get_object_or_404

from gissues.extensions.github.models import Comments, Issue, IssueCommentBody, Repository
from gissues.extensions.github.serializers import CommentsSerializer, IssueSerializer, RepositorySerializer
from gissues.extensions.github.transformers import transform_comments, transform_issue, transform_repository
from gissues.extensions.github_client.client import github_client
from gissues.extensions.github_client.views import GitHubClientViewSet


class RepositoryViewSet(GitHubClientViewSet):
    serializer_class = RepositorySerializer
    queryset = Repository.objects.all()
    lookup_field = "name"
    lookup_url_kwarg = "repository_name"
    ordering = ["name"]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner_name=self.kwargs["repository_owner"])

    def get_object(self):
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


class IssueViewSet(GitHubClientViewSet):
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()
    lookup_field = "number"
    lookup_url_kwarg = "issue_number"
    ordering = ["number"]

    def get_queryset(self):
        qs = super().get_queryset()
        repository = get_object_or_404(Repository, name=self.kwargs["repository_repository_name"])

        qs = qs.annotate(body_text=Subquery(IssueCommentBody.objects.filter(issue=OuterRef("pk")).values("body")[:1]))

        return qs.filter(repository=repository)

    def get_object(self):
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

        transformed_data = transform_issue(obj, self.kwargs["repository_repository_name"]).dict()
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

    def get_queryset(self):
        qs = super().get_queryset()
        issue = get_object_or_404(Issue, number=self.kwargs["issue_issue_number"])

        qs = qs.annotate(body_text=Subquery(IssueCommentBody.objects.filter(comment=OuterRef("pk")).values("body")[:1]))

        return qs.filter(issue=issue)

    def get_object(self):
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
