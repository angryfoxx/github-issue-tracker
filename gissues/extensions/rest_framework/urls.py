from rest_framework.routers import DefaultRouter

from gissues.extensions.rest_framework.views import MetaViewSet

router = DefaultRouter()

router.register("meta", MetaViewSet, basename="meta")

urlpatterns = router.urls
