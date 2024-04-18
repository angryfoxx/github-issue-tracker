import importlib
import logging
from pathlib import Path

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from gissues.extensions.rest_framework.views import MetaViewSet

logger = logging.getLogger(__name__)

router = DefaultRouter()

router.register("meta", MetaViewSet, basename="meta")

extensions = [x for x in Path("gissues/extensions").glob("*") if x.stem != "__pycache__" and x.is_dir()]

nested_urls = []
for extension in extensions:
    module_name = extension.name
    try:
        module = importlib.import_module(f"gissues.extensions.{module_name}.urls")
        app_router = getattr(module, "router", None)
        nested = getattr(module, "nested_urls", None)

        if nested is not None:
            nested_urls.extend(nested)

        if app_router is not None:
            router.registry.extend(app_router.registry)

    except ModuleNotFoundError:
        logger.debug(
            "rest_framework: URL file not found for %s extension." " Extension may not working properly.",
            module_name,
        )


urlpatterns = [path("", include(router.urls + nested_urls))]
