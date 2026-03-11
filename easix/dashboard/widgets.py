"""
Dashboard Widgets
Modular and configurable widgets for the dashboard.
"""
from django.apps import apps
from django.db import models
from django.db.models import Count, Sum, Avg, Max, Min
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Any, Optional, Callable


class Widget:
    """Base widget class for dashboard."""
    
    template = "easix/widgets/base.html"
    width = "full"  # full, half, third, quarter
    height = "default"  # default, tall, short
    
    def __init__(self, title: str, icon: str = "chart-bar", **kwargs):
        self.title = title
        self.icon = icon
        self.options = kwargs
    
    def get_context(self, request) -> Dict[str, Any]:
        """Get widget context data."""
        return {
            "title": self.title,
            "icon": self.icon,
            "options": self.options,
        }
    
    def render(self, request) -> Dict[str, Any]:
        """Render widget and return context."""
        return {
            "template": self.template,
            "context": self.get_context(request),
            "width": self.width,
            "height": self.height,
        }


class StatWidget(Widget):
    """Display a single statistic with optional trend."""
    
    template = "easix/widgets/stat.html"
    width = "quarter"
    
    def __init__(self, title: str, value: Any, icon: str = "chart-bar",
                 trend: Optional[float] = None, trend_label: str = "vs last period",
                 subtitle: str = "", **kwargs):
        super().__init__(title, icon, **kwargs)
        self.value = value
        self.trend = trend
        self.trend_label = trend_label
        self.subtitle = subtitle
    
    def get_context(self, request) -> Dict[str, Any]:
        context = super().get_context(request)
        context.update({
            "value": self.value,
            "trend": self.trend,
            "trend_label": self.trend_label,
            "subtitle": self.subtitle,
        })
        return context


class ModelCountWidget(StatWidget):
    """Display count of model instances."""
    
    def __init__(self, model: str, title: Optional[str] = None,
                 icon: str = "users", filter_func: Optional[Callable] = None, **kwargs):
        self.model_path = model
        self.filter_func = filter_func
        
        try:
            app_label, model_name = model.split(".")
            model_class = apps.get_model(app_label, model_name)
            self.model_class = model_class
            display_title = title or model_class._meta.verbose_name_plural.title()
        except (ValueError, LookupError):
            display_title = title or "Items"
            self.model_class = None
        
        super().__init__(title=display_title, value=0, icon=icon, **kwargs)
    
    def get_context(self, request) -> Dict[str, Any]:
        context = super().get_context(request)
        
        if self.model_class:
            queryset = self.model_class.objects.all()
            if self.filter_func:
                queryset = self.filter_func(queryset, request)
            
            count = queryset.count()
            context["value"] = count
            
            # Calculate trend (last 7 days vs previous 7 days)
            now = timezone.now()
            recent = queryset.filter(
                created_at__gte=now - timedelta(days=7)
            ).count() if hasattr(self.model_class, "created_at") else 0
            
            previous = queryset.filter(
                created_at__gte=now - timedelta(days=14),
                created_at__lt=now - timedelta(days=7)
            ).count() if hasattr(self.model_class, "created_at") else 0
            
            if previous > 0:
                trend = ((recent - previous) / previous) * 100
                context["trend"] = round(trend, 1)
            elif recent > 0:
                context["trend"] = 100
        
        return context


class ChartWidget(Widget):
    """Display a chart (line, bar, pie)."""
    
    template = "easix/widgets/chart.html"
    width = "half"
    chart_type = "line"  # line, bar, pie, doughnut
    
    def __init__(self, title: str, data: Optional[Dict] = None,
                 chart_type: str = "line", height: str = "default", **kwargs):
        super().__init__(title, "chart-bar", **kwargs)
        self.data = data or {"labels": [], "datasets": []}
        self.chart_type = chart_type
        self.height = height
    
    def get_context(self, request) -> Dict[str, Any]:
        context = super().get_context(request)
        context["chart_data"] = self.data
        context["chart_type"] = self.chart_type
        return context


class ModelChartWidget(ChartWidget):
    """Display chart based on model data."""
    
    def __init__(self, model: str, title: str, x_field: str, y_field: str,
                 chart_type: str = "line", aggregate: str = "count",
                 days: int = 30, **kwargs):
        self.model_path = model
        self.x_field = x_field
        self.y_field = y_field
        self.aggregate = aggregate
        self.days = days
        
        try:
            app_label, model_name = model.split(".")
            self.model_class = apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            self.model_class = None
        
        super().__init__(title=title, chart_type=chart_type, **kwargs)
    
    def get_context(self, request) -> Dict[str, Any]:
        context = super().get_context(request)
        
        if self.model_class:
            labels = []
            data = []
            
            now = timezone.now()
            for i in range(self.days - 1, -1, -1):
                date = now - timedelta(days=i)
                labels.append(date.strftime("%b %d"))
                
                date_start = date.replace(hour=0, minute=0, second=0)
                date_end = date.replace(hour=23, minute=59, second=59)
                
                queryset = self.model_class.objects.filter(
                    created_at__range=[date_start, date_end]
                ) if hasattr(self.model_class, "created_at") else self.model_class.objects.none()
                
                if self.aggregate == "count":
                    value = queryset.count()
                elif self.aggregate == "sum":
                    value = queryset.aggregate(Sum(self.y_field))[f"{self.y_field}__sum"] or 0
                elif self.aggregate == "avg":
                    value = queryset.aggregate(Avg(self.y_field))[f"{self.y_field}__avg"] or 0
                else:
                    value = queryset.count()
                
                data.append(value)
            
            context["chart_data"] = {
                "labels": labels,
                "datasets": [{
                    "label": self.title,
                    "data": data,
                    "borderColor": self.options.get("color", "#6366f1"),
                    "backgroundColor": self.options.get("color", "#6366f1") + "20",
                    "tension": 0.4,
                    "fill": True,
                }]
            }
        
        return context


class RecentItemsWidget(Widget):
    """Display recent items from a model."""
    
    template = "easix/widgets/recent_items.html"
    width = "half"
    
    def __init__(self, model: str, title: Optional[str] = None,
                 limit: int = 5, display_field: Optional[str] = None, **kwargs):
        self.model_path = model
        self.limit = limit
        self.display_field = display_field
        
        try:
            app_label, model_name = model.split(".")
            model_class = apps.get_model(app_label, model_name)
            self.model_class = model_class
            display_title = title or f"Recent {model_class._meta.verbose_name_plural.title()}"
        except (ValueError, LookupError):
            display_title = title or "Recent Items"
            self.model_class = None
        
        super().__init__(title=display_title, icon="clock", **kwargs)
    
    def get_context(self, request) -> Dict[str, Any]:
        context = super().get_context(request)
        
        if self.model_class:
            items = self.model_class.objects.all().order_by("-pk")[:self.limit]
            context["items"] = [
                {
                    "pk": item.pk,
                    "str": str(item),
                    "display": getattr(item, self.display_field, "") if self.display_field else str(item),
                }
                for item in items
            ]
            context["model_app"] = self.model_class._meta.app_label
            context["model_name"] = self.model_class._meta.model_name
        
        return context


class QuickActionsWidget(Widget):
    """Display quick action buttons."""
    
    template = "easix/widgets/quick_actions.html"
    width = "quarter"
    
    def __init__(self, title: str = "Quick Actions", actions: Optional[List[Dict]] = None, **kwargs):
        self.actions = actions or []
        super().__init__(title=title, icon="lightning", **kwargs)
    
    def get_context(self, request) -> Dict[str, Any]:
        context = super().get_context(request)
        context["actions"] = self.actions
        return context


class ActivityWidget(Widget):
    """Display recent activity."""
    
    template = "easix/widgets/activity.html"
    width = "half"
    
    def __init__(self, title: str = "Recent Activity", limit: int = 10, **kwargs):
        self.limit = limit
        super().__init__(title=title, icon="activity", **kwargs)
    
    def get_context(self, request) -> Dict[str, Any]:
        context = super().get_context(request)
        
        try:
            from ..activity.models import ActivityLog
            activities = ActivityLog.objects.all().select_related("user")[:self.limit]
            context["activities"] = activities
        except (ImportError, Exception):
            context["activities"] = []
        
        return context


# Pre-built widget configurations
DEFAULT_WIDGETS = [
    # First row - Stats
    {"widget": ModelCountWidget, "args": {"model": "auth.User", "icon": "users"}},
    {"widget": ModelCountWidget, "args": {"model": "auth.User", "icon": "user-plus"}},
    {"widget": StatWidget, "args": {"title": "Total Revenue", "value": "$0", "icon": "currency-dollar"}},
    {"widget": StatWidget, "args": {"title": "Active Now", "value": "0", "icon": "users"}},
    
    # Second row - Charts and lists
    {"widget": RecentItemsWidget, "args": {"model": "auth.User", "limit": 5}},
    {"widget": QuickActionsWidget, "args": {
        "actions": [
            {"label": "Create User", "icon": "user-plus", "url": "#"},
            {"label": "View Reports", "icon": "chart-bar", "url": "#"},
            {"label": "Settings", "icon": "cog", "url": "#"},
        ]
    }},
]
