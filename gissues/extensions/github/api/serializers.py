from rest_framework import serializers

from gissues.extensions.github.models import Comments, Issue, Repository


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = "__all__"


class IssueSerializer(serializers.ModelSerializer):
    body = serializers.CharField(source="body_text")

    class Meta:
        model = Issue
        fields = (
            "id",
            "title",
            "number",
            "body",
            "is_closed",
            "closed_at",
            "state_reason",
            "is_locked",
            "lock_reason",
            "created_at",
            "updated_at",
        )


class CommentsSerializer(serializers.ModelSerializer):
    body = serializers.CharField(source="body_text")

    class Meta:
        model = Comments
        fields = (
            "id",
            "comment_id",
            "body",
            "created_at",
            "updated_at",
        )
