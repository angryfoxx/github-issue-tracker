from typing import Any, Optional

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field

from gissues.extensions.github.models import Comments, Issue, Repository


class RepositorySerializer(serializers.ModelSerializer[Repository]):
    class Meta:
        model = Repository
        fields = "__all__"


class IssueSerializer(serializers.ModelSerializer[Issue]):
    class Meta:
        model = Issue
        fields = (
            "id",
            "title",
            "number",
            "body",
            "is_closed",
            "state_reason",
            "is_locked",
            "lock_reason",
            "comment_count",
            "closed_at",
            "created_at",
            "updated_at",
        )


class CommentsSerializer(serializers.ModelSerializer[Comments]):
    class Meta:
        model = Comments
        fields = (
            "id",
            "comment_id",
            "body",
            "created_at",
            "updated_at",
        )


class HistorySerializer(serializers.Serializer):
    history_id = serializers.IntegerField()
    history_date = serializers.DateTimeField()
    changes = serializers.SerializerMethodField()

    @extend_schema_field(serializers.DictField)
    def get_changes(self, instance):
        next_record = instance.next_record
        return {change.field: change.old for change in next_record.diff_against(instance).changes}


class BaseHistorySerializer(serializers.Serializer):
    original = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    instance_serializer_mapping = {
        Issue: IssueSerializer,
        Repository: RepositorySerializer,
        Comments: CommentsSerializer,
    }

    @extend_schema_field(serializers.DictField)
    def get_original(self, instance) -> dict[str, Any]:
        serializer = self.instance_serializer_mapping.get(instance.__class__)
        return serializer(instance, context=self.context).data

    @extend_schema_field(HistorySerializer(many=True))
    def get_history(self, instance) -> Optional[list[dict[str, Any]]]:
        # Exclude the latest history entry
        # Because the latest history entry is the current state of the object
        history = instance.history.exclude(history_id=instance.history.latest("history_id").history_id)
        return HistorySerializer(history, context=self.context, many=True).data
