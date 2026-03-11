"""
Easix Main Views
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.utils import get_fields_from_path
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def get_easix_settings():
    """Get Easix settings from app config."""
    from django.apps import apps
    easix_config = apps.get_app_config("easix")
    return easix_config.easix_settings


def get_registered_models():
    """Get all models that should be visible in Easix."""
    from django.apps import apps
    
    registered = []
    for model in apps.get_models():
        # Skip certain internal models
        if model._meta.app_label in ["contenttypes", "sessions", "admin", "auth"]:
            continue
        if model._meta.abstract:
            continue
            
        registered.append({
            "model": model,
            "app_label": model._meta.app_label,
            "model_name": model._meta.model_name,
            "verbose_name": model._meta.verbose_name,
            "verbose_name_plural": model._meta.verbose_name_plural,
        })
    
    return sorted(registered, key=lambda x: x["verbose_name"])


def global_search(request):
    """Global search across all registered models."""
    easix_settings = get_easix_settings()
    
    if not easix_settings["ENABLE_GLOBAL_SEARCH"]:
        return redirect("easix:dashboard")
    
    query = request.GET.get("q", "")
    results = []
    
    if query and len(query) >= 2:
        search_models = easix_settings.get("SEARCH_MODELS", [])
        
        # If no specific models configured, search all registered models
        if not search_models:
            search_models = [
                f"{m['app_label']}.{m['model_name']}" 
                for m in get_registered_models()
            ]
        
        for model_path in search_models[:10]:  # Limit to 10 models
            try:
                app_label, model_name = model_path.split(".")
                model = apps.get_model(app_label, model_name)
                
                # Search in text fields
                search_fields = []
                for field in model._meta.fields:
                    if isinstance(field, (models.CharField, models.TextField)):
                        search_fields.append(field.name)
                
                if search_fields:
                    from django.db.models import Q
                    q_objects = Q()
                    for field in search_fields[:5]:  # Limit fields
                        q_objects |= Q(**{f"{field}__icontains": query})
                    
                    items = model.objects.filter(q_objects)[:5]
                    for item in items:
                        results.append({
                            "model": model._meta.verbose_name,
                            "app_label": app_label,
                            "model_name": model_name,
                            "item": str(item),
                            "pk": item.pk,
                        })
            except (LookupError, ValueError):
                continue
    
    context = {
        "query": query,
        "results": results,
        "easix_settings": easix_settings,
    }
    
    if request.htmx:
        return render(request, "easix/pages/search_results.html", context)
    
    return render(request, "easix/pages/search.html", context)


def search_models(request):
    """Get search suggestions for models."""
    query = request.GET.get("q", "")
    suggestions = []
    
    if query and len(query) >= 2:
        for model_info in get_registered_models():
            suggestions.append({
                "name": model_info["verbose_name"],
                "app_label": model_info["app_label"],
                "model_name": model_info["model_name"],
            })
    
    return JsonResponse({"suggestions": suggestions[:10]})


def file_upload(request):
    """Handle file uploads with progress."""
    if request.method == "POST":
        file = request.FILES.get("file")
        if file:
            # Return file info for client-side handling
            return JsonResponse({
                "success": True,
                "filename": file.name,
                "size": file.size,
                "type": file.content_type,
            })
    
    return JsonResponse({"success": False, "error": "No file provided"})


def settings_view(request):
    """Easix settings page."""
    easix_settings = get_easix_settings()
    
    context = {
        "easix_settings": easix_settings,
        "models": get_registered_models(),
    }
    
    return render(request, "easix/pages/settings.html", context)
