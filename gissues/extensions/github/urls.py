from rest_framework.routers import SimpleRouter

from rest_framework_nested.routers import NestedSimpleRouter

from gissues.extensions.github.api.views import CommentsViewSet, IssueViewSet, RepositoryViewSet

router = SimpleRouter()

router.register(r"repositories/(?P<repository_owner>\w+)", RepositoryViewSet, basename="repository")

repo_nested_router = NestedSimpleRouter(router, r"repositories/(?P<repository_owner>\w+)", lookup="repository")

repo_nested_router.register("issues", IssueViewSet, basename="repository-issues")

issue_nested_router = NestedSimpleRouter(repo_nested_router, r"issues", lookup="issue")

issue_nested_router.register("comments", CommentsViewSet, basename="issue-comments")

urlpatterns = router.urls + repo_nested_router.urls + issue_nested_router.urls
