"""
Dashboard Views
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from typing import List, Dict, Any

from ..views import get_easix_settings, get_registered_models
from .widgets import DEFAULT_WIDGETS


def get_dashboard_widgets(request) -> List[Dict[str, Any]]:
    """Get configured dashboard widgets."""
    easix_settings = get_easix_settings()
    widget_configs = easix_settings.get("DASHBOARD_WIDGETS", DEFAULT_WIDGETS)
    
    widgets = []
    for config in widget_configs:
        widget_class = config.get("widget")
        args = config.get("args", {})
        kwargs = config.get("kwargs", {})
        
        try:
            widget = widget_class(**args, **kwargs)
            widgets.append(widget.render(request))
        except Exception:
            continue
    
    return widgets


@staff_member_required
def dashboard(request):
    """Main dashboard view."""
    easix_settings = get_easix_settings()
    widgets = get_dashboard_widgets(request)
    models = get_registered_models()
    
    context = {
        "easix_settings": easix_settings,
        "widgets": widgets,
        "models": models,
        "page_title": easix_settings["SITE_TITLE"],
    }
    
    return render(request, "easix/pages/dashboard.html", context)
