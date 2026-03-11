"""
Test URLs for Easix.
"""
from django.urls import path, include

urlpatterns = [
    path("admin/", include("easix.urls", namespace="easix")),
]
