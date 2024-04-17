from gissues.settings import *  # noqa: F403

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
INSTALLED_APPS.remove("django_extensions")  # noqa: F405
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
