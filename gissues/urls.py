from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from gissues.extensions.utils import APIRootView

api_urls: list[URLPattern | URLResolver] = [
    path("", APIRootView.as_view(), name="api-root"),
    path("", include("gissues.extensions.rest_framework.urls")),
    path("", include("gissues.extensions.auth.urls")),
    path("", include("gissues.extensions.github.urls")),
]

urlpatterns: list[URLResolver | URLPattern] = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include((api_urls, "api"))),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema",
        ),
        name="redoc",
    ),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(),
        name="swagger-ui",
    ),
]


if settings.IS_LOCAL_ENV:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
