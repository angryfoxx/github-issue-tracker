from rest_framework.routers import SimpleRouter

from gissues.extensions.auth.api.views import UserRepositoryFollowViewSet

router = SimpleRouter()

router.register("following-repositories", UserRepositoryFollowViewSet, basename="following-repositories")

urlpatterns = router.urls
