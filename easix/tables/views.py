"""
Table Views
Handle table data, sorting, filtering, pagination, and bulk actions.
"""
import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.admin.utils import get_fields_from_path
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.utils import timezone
from typing import Any, Dict, List, Optional

from ..views import get_easix_settings
from .config import TableConfig, Column, Action, BulkAction


def get_table_config(model: Any) -> TableConfig:
    """Get or create table config for model."""
    # Check for custom config in model's Meta
    if hasattr(model, "easix_table_config"):
        return model.easix_table_config
    
    # Auto-generate config
    return TableConfig.from_model(model)


def apply_search(queryset, config: TableConfig, search_query: str):
    """Apply search to queryset."""
    if not search_query or not config.search_fields:
        return queryset
    
    q_objects = Q()
    for field_name in config.search_fields:
        q_objects |= Q(**{f"{field_name}__icontains": search_query})
    
    return queryset.filter(q_objects)


def apply_filters(queryset, config: TableConfig, filters: Dict[str, Any]):
    """Apply filters to queryset."""
    for filter_config in config.filters:
        value = filters.get(filter_config.field)
        if value is None or value == "":
            continue
        
        if filter_config.type == "boolean":
            if value == "true":
                queryset = queryset.filter(**{filter_config.field: True})
            elif value == "false":
                queryset = queryset.filter(**{filter_config.field: False})
        elif filter_config.type == "date_range":
            if value.get("start"):
                queryset = queryset.filter(**{f"{filter_config.field}__gte": value["start"]})
            if value.get("end"):
                queryset = queryset.filter(**{f"{filter_config.field}__lte": value["end"]})
        elif filter_config.type in ("select", "multiselect"):
            if filter_config.type == "multiselect" and isinstance(value, list):
                queryset = queryset.filter(**{f"{filter_config.field}__in": value})
            else:
                queryset = queryset.filter(**{filter_config.field: value})
        else:
            queryset = queryset.filter(**{filter_config.field: value})
    
    return queryset


def apply_sorting(queryset, config: TableConfig, sort_field: str):
    """Apply sorting to queryset."""
    if not sort_field:
        sort_field = config.default_sort
    
    # Validate sort field
    valid_fields = [col.field for col in config.columns if col.sortable]
    valid_fields.extend([f"-{f}" for f in valid_fields])
    
    if sort_field in valid_fields or sort_field.lstrip("-") in [col.field for col in config.columns]:
        return queryset.order_by(sort_field)
    
    return queryset.order_by(config.default_sort)


def apply_pagination(queryset, page: int, per_page: int):
    """Apply pagination to queryset."""
    start = (page - 1) * per_page
    end = start + per_page
    return queryset[start:end]


def table_data(request, app_label: str, model_name: str):
    """Get table data as JSON for HTMX/Alpine."""
    from django.apps import apps
    
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return JsonResponse({"error": "Model not found"}, status=404)
    
    config = get_table_config(model)
    
    # Get query parameters
    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", config.per_page))
    sort = request.GET.get("sort", config.default_sort)
    search = request.GET.get("search", "")
    
    # Get filters
    filters = {}
    for filter_config in config.filters:
        value = request.GET.get(f"filter_{filter_config.field}")
        if value:
            filters[filter_config.field] = value
    
    # Build queryset
    queryset = model.objects.all()
    
    # Apply custom queryset if defined
    if config.get_queryset:
        queryset = config.get_queryset(queryset, request)
    
    # Apply search, filters, sorting
    queryset = apply_search(queryset, config, search)
    queryset = apply_filters(queryset, config, filters)
    queryset = apply_sorting(queryset, config, sort)
    
    # Get total count before pagination
    total = queryset.count()
    
    # Apply pagination
    queryset = apply_pagination(queryset, page, per_page)
    
    # Build row data
    rows = []
    for obj in queryset:
        row_data = {
            "pk": obj.pk,
            "str": str(obj),
            "cells": {},
        }
        
        for col in config.columns:
            value = col.get_value(obj)
            
            # Handle badge formatting
            if col.badge and value in col.badge:
                value = {
                    "value": value,
                    "badge": col.badge[value],
                }
            
            row_data["cells"][col.field] = value
        
        rows.append(row_data)
    
    return JsonResponse({
        "rows": rows,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
        "columns": [
            {
                "field": col.field,
                "label": col.label,
                "sortable": col.sortable,
                "visible": col.visible,
                "type": col.type,
                "width": col.width,
                "align": col.align,
            }
            for col in config.columns
        ],
        "filters": [
            {
                "field": f.field,
                "label": f.label,
                "type": f.type,
                "options": f.options,
                "default": f.default,
            }
            for f in config.filters
        ],
        "actions": [
            {
                "label": action.label,
                "icon": action.icon,
                "style": action.style,
                "confirm": action.confirm,
            }
            for action in config.actions
        ],
        "bulk_actions": [
            {
                "label": action.label,
                "icon": action.icon,
                "style": action.style,
                "confirm": action.confirm,
            }
            for action in config.bulk_actions
        ],
    })


def model_list(request, app_label: str, model_name: str):
    """Render model list page with table."""
    from django.apps import apps
    
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, "Model not found.")
        return redirect("easix:dashboard")
    
    config = get_table_config(model)
    easix_settings = get_easix_settings()
    
    context = {
        "model": model,
        "app_label": app_label,
        "model_name": model_name,
        "config": config,
        "easix_settings": easix_settings,
        "page_title": model._meta.verbose_name_plural.title(),
        "add_label": f"Create New {model._meta.verbose_name.title()}",
        "create_url": reverse("easix:model_create", args=[app_label, model_name]),
    }
    
    return render(request, "easix/pages/model_list.html", context)


def bulk_action(request, app_label: str, model_name: str):
    """Handle bulk actions."""
    from django.apps import apps
    
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return JsonResponse({"error": "Model not found"}, status=404)
    
    config = get_table_config(model)
    
    action_name = request.POST.get("action")
    selected_ids = request.POST.getlist("selected_ids", [])
    
    if not action_name or not selected_ids:
        return JsonResponse({"error": "Invalid request"}, status=400)
    
    # Find bulk action config
    bulk_action_config = None
    for ba in config.bulk_actions:
        if ba.action_name == action_name:
            bulk_action_config = ba
            break
    
    if not bulk_action_config:
        return JsonResponse({"error": "Action not found"}, status=404)
    
    # Execute action
    queryset = model.objects.filter(pk__in=selected_ids)
    count = queryset.count()
    
    if action_name == "delete_selected":
        queryset.delete()
        messages.success(request, f"Successfully deleted {count} items.")
    else:
        messages.error(request, "Unknown bulk action.")
    
    if request.htmx:
        return JsonResponse({"success": True, "message": f"{count} items processed."})
    
    return redirect("easix:model_list", app_label=app_label, model_name=model_name)


def export_csv(request, app_label: str, model_name: str):
    """Export table data as CSV."""
    from django.apps import apps
    
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, "Model not found.")
        return redirect("easix:dashboard")
    
    config = get_table_config(model)
    
    # Get current filters/search
    search = request.GET.get("search", "")
    
    queryset = model.objects.all()
    queryset = apply_search(queryset, config, search)
    
    # Create CSV response
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{model_name}_export.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    headers = [col.label for col in config.columns if col.visible]
    writer.writerow(headers)
    
    # Write data
    for obj in queryset:
        row = []
        for col in config.columns:
            if col.visible:
                value = col.get_value(obj)
                if isinstance(value, bool):
                    value = "Yes" if value else "No"
                elif value is None:
                    value = ""
                row.append(str(value))
        writer.writerow(row)
    
    return response
