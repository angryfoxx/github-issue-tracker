from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

urlpatterns: list[URLResolver | URLPattern] = [
    path("admin/", admin.site.urls),
    path("api/", include("gissues.extensions.rest_framework.urls")),
    path("api-auth/", include("rest_framework.urls")),
]


if settings.IS_LOCAL_ENV:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
