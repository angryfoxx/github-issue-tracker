import datetime
import logging

from django.core.mail import send_mail

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

    bulk_create = []
    for comment in comments:
        old_comment = Comments.objects.filter(comment_id=comment["id"]).first()

        if old_comment is None or old_comment.updated_at.isoformat().replace("+00:00", "Z") != comment["updated_at"]:
            transformed_data = transform_comments(comment, issue_number)
            bulk_create.append(Comments(**transformed_data.dict()))

    Comments.objects.bulk_create(
        bulk_create,
        update_conflicts=True,
        update_fields=[
            "body",
            "created_at",
            "updated_at",
        ],
        unique_fields=["comment_id"],
    )
    return None


@app.task
def IssueAdapterTask(owner_name: str, repository_name: str, following_date: datetime.datetime, user_email: str) -> None:
    issue_response = github_client.issues.list(owner_name, repository_name)

    if not issue_response.is_ok:
        logger.error(f"Failed to fetch issues from {owner_name}/{repository_name}")
        return None

    issues = issue_response.content

    bulk_create = []
    for issue in issues:
        old_issue = Issue.objects.filter(number=issue["number"]).first()

        if old_issue is None or old_issue.updated_at.isoformat().replace("+00:00", "Z") != issue["updated_at"]:
            transformed_data = transform_issue(issue, repository_name, owner_name)
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

    Issue.objects.bulk_create(
        bulk_create,
        update_conflicts=True,
        update_fields=[
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
        unique_fields=["number"],
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
