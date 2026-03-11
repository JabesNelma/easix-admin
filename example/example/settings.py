"""
Django settings for Easix Example project.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-example-key-change-in-production"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Easix Admin
    "easix",
    # Example app
    "myapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "easix.activity.signals.ActivityMiddleware",  # For activity logging
]

ROOT_URLCONF = "example.urls"

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

WSGI_APPLICATION = "example.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Easix Configuration
EASIX_SITE_TITLE = "Easix Demo Dashboard"
EASIX_SITE_BRAND = "Easix"
EASIX_ENABLE_ACTIVITY_LOG = True
EASIX_ENABLE_GLOBAL_SEARCH = True
EASIX_TABLE_PER_PAGE = 25

# Models to search
EASIX_SEARCH_MODELS = [
    "myapp.Product",
    "myapp.Order",
    "myapp.Customer",
    "auth.User",
]

# Custom dashboard widgets
EASIX_DASHBOARD_WIDGETS = [
    # Stats row
    {"widget": "easix.dashboard.widgets.ModelCountWidget", "args": {"model": "myapp.Product", "icon": "photograph"}},
    {"widget": "easix.dashboard.widgets.ModelCountWidget", "args": {"model": "myapp.Order", "icon": "document-text"}},
    {"widget": "easix.dashboard.widgets.ModelCountWidget", "args": {"model": "myapp.Customer", "icon": "users"}},
    {"widget": "easix.dashboard.widgets.ModelCountWidget", "args": {"model": "auth.User", "icon": "user-plus"}},
    
    # Charts and lists
    {"widget": "easix.dashboard.widgets.RecentItemsWidget", "args": {"model": "myapp.Order", "limit": 5}},
    {"widget": "easix.dashboard.widgets.QuickActionsWidget", "args": {
        "actions": [
            {"label": "New Product", "icon": "plus", "url": "/admin/models/myapp/product/create/"},
            {"label": "New Order", "icon": "plus", "url": "/admin/models/myapp/order/create/"},
            {"label": "New Customer", "icon": "plus", "url": "/admin/models/myapp/customer/create/"},
            {"label": "View Reports", "icon": "chart-bar", "url": "#"},
        ]
    }},
    {"widget": "easix.dashboard.widgets.ActivityWidget", "args": {"limit": 5}},
]
