import datetime
import logging

from django.core.mail import send_mail

from simple_history.utils import bulk_create_with_history, bulk_update_with_history

from gissues.celery import app
from gissues.extensions.github.models import Comments, Issue, Repository
from gissues.extensions.github.transformers import transform_comments, transform_issue
from gissues.extensions.github_client.client import github_client

logger = logging.getLogger(__name__)


@app.task
def send_email(subject: str, message: str, user_email: str) -> None:
    send_mail(
        subject,
        message,
        "gissues@localhost.com",
        [user_email],
    )
    return None


@app.task
def CommentAdapterTask(owner: str, repository_name: str, issue_number: int | str):
    comment_response = github_client.comments.list(owner, repository_name, issue_number)

    if not comment_response.is_ok:
        logger.error(f"Failed to fetch comments for issue {issue_number} from {owner}/{repository_name}")
        return None

    comments = comment_response.content

    comments_mapping_with_id = Comments.objects.filter(issue__number=issue_number).in_bulk(field_name="comment_id")

    bulk_create, bulk_update = [], []
    for comment in comments:
        old_comment = Comments.objects.filter(comment_id=comment["id"]).first()

        if old_comment is None or old_comment.updated_at.isoformat().replace("+00:00", "Z") != comment["updated_at"]:
            transformed_data = transform_comments(comment, issue_number)

            if transformed_data.comment_id in comments_mapping_with_id:
                obj = comments_mapping_with_id[transformed_data.comment_id]
                obj.body = transformed_data.body
                obj.created_at = transformed_data.created_at
                obj.updated_at = transformed_data.updated_at
                bulk_update.append(obj)
            else:
                bulk_create.append(Comments(**transformed_data.dict()))

    bulk_create_with_history(bulk_create, Comments, batch_size=1000)
    bulk_update_with_history(bulk_update, Comments, ["body", "created_at", "updated_at"], batch_size=1000)
    return None


@app.task
def IssueAdapterTask(owner_name: str, repository_name: str, following_date: datetime.datetime, user_email: str) -> None:
    issue_response = github_client.issues.list(owner_name, repository_name)

    if not issue_response.is_ok:
        logger.error(f"Failed to fetch issues from {owner_name}/{repository_name}")
        return None

    issues = issue_response.content

    issues_mapping_with_number = Issue.objects.filter(
        repository__owner_name=owner_name, repository__name=repository_name
    ).in_bulk(field_name="number")

    bulk_create, bulk_update = [], []
    for issue in issues:
        old_issue = Issue.objects.filter(number=issue["number"]).first()

        if old_issue is None or old_issue.updated_at.isoformat().replace("+00:00", "Z") != issue["updated_at"]:
            transformed_data = transform_issue(issue, repository_name, owner_name)

            if transformed_data.number in issues_mapping_with_number:
                obj = issues_mapping_with_number[transformed_data.number]
                obj.title = transformed_data.title
                obj.body = transformed_data.body
                obj.is_closed = transformed_data.is_closed
                obj.closed_at = transformed_data.closed_at
                obj.state_reason = transformed_data.state_reason
                obj.is_locked = transformed_data.is_locked
                obj.lock_reason = transformed_data.lock_reason
                obj.comment_count = transformed_data.comment_count
                obj.created_at = transformed_data.created_at
                obj.updated_at = transformed_data.updated_at
                bulk_update.append(obj)
            else:
                bulk_create.append(Issue(**transformed_data.dict()))

            if transformed_data.comment_count > 0:
                CommentAdapterTask.apply_async(
                    args=(owner_name, repository_name, issue["number"]),
                )

            # Don't send email if the issue was created before the following date
            converted_created_at = datetime.datetime.strptime(
                transformed_data.created_at, "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=datetime.timezone.utc)
            converted_updated_at = datetime.datetime.strptime(
                transformed_data.updated_at, "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=datetime.timezone.utc)
            if converted_created_at > following_date or converted_updated_at > following_date:
                send_email.apply_async(
                    args=(
                        f"New Issue Notification on {owner_name}/{repository_name}",
                        "Hello,\n\n"
                        "A new issue has been created or updated in one of the repositories you're following.\n"
                        "Please check it out for more details.\n\n"
                        f"Repository: {owner_name}/{repository_name}\n"
                        f"Title: {transformed_data.title}\n"
                        f"Issue Number: {transformed_data.number}\n\n"
                        "Best regards,\n"
                        "Github Issues Tracker Team",
                        user_email,
                    ),
                )

    bulk_create_with_history(bulk_create, Issue, batch_size=1000)
    bulk_update_with_history(
        bulk_update,
        Issue,
        [
            "title",
            "body",
            "is_closed",
            "closed_at",
            "state_reason",
            "is_locked",
            "lock_reason",
            "comment_count",
            "created_at",
            "updated_at",
        ],
        batch_size=1000,
    )
    return None


@app.task(name="gissues.extensions.github_client.tasks.CheckForNewIssues")
def CheckForNewIssues() -> None:
    repositories = Repository.objects.filter(
        followers__isnull=False,
    ).values_list("owner_name", "name", "followers__created_at", "followers__user__email")

    for owner_name, repository_name, following_date, user_email in repositories:
        IssueAdapterTask.apply_async(
            args=(owner_name, repository_name, following_date, user_email),
        )

    return None
