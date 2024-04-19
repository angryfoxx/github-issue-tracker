from rest_framework.routers import SimpleRouter

from gissues.extensions.rest_framework.api.views import MetaViewSet

router = SimpleRouter()

router.register("meta", MetaViewSet, basename="meta")

urlpatterns = router.urls
