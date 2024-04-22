from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "cango-insecure-fyzoyrv2av$%^-@k-w%je9b-bu_)^1md_5lor%jg*am*"
DEBUG = False
ALLOWED_HOSTS = ["*"]
SERVER_TYPE = "test"
IS_LOCAL_ENV = DEBUG and SERVER_TYPE == "local"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "django_filters",
    "simple_history",
    # Local apps
    "gissues",
    "gissues.extensions",
    "gissues.extensions.auth",
    "gissues.extensions.github",
    "gissues.extensions.github_client",
    "gissues.extensions.rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Third party middleware
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "gissues.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "gissues.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

AUTH_USER_MODEL = "account.User"

REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.AcceptHeaderVersioning",
    "DEFAULT_VERSION": "alpha",
    "ALLOWED_VERSIONS": ["alpha"],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": (
        "rest_framework.renderers.MultiPartRenderer",
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "URL_FORMAT_OVERRIDE": None,
}

CHECK_FOR_NEW_ISSUES_INTERVAL_IN_MINUTES = 60  # DEFAULT: 1 hour

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 25

GITHUB_CLIENT_URL = "https://www.test.com"
GITHUB_CLIENT_AUTH_TOKEN = ""
