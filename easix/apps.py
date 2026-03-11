"""
Easix Admin Framework Configuration
"""
from django.apps import AppConfig
from django.conf import settings


class EasixConfig(AppConfig):
    """Main configuration for the Easix admin framework."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "easix"
    verbose_name = "Easix Admin"
    
    # Easix configuration options
    easix_settings = {
        "SITE_TITLE": getattr(settings, "EASIX_SITE_TITLE", "Admin Dashboard"),
        "SITE_BRAND": getattr(settings, "EASIX_SITE_BRAND", "Easix"),
        "SITE_LOGO": getattr(settings, "EASIX_SITE_LOGO", None),
        "DASHBOARD_PER_PAGE": getattr(settings, "EASIX_DASHBOARD_PER_PAGE", 10),
        "TABLE_PER_PAGE": getattr(settings, "EASIX_TABLE_PER_PAGE", 25),
        "ENABLE_ACTIVITY_LOG": getattr(settings, "EASIX_ENABLE_ACTIVITY_LOG", True),
        "ENABLE_GLOBAL_SEARCH": getattr(settings, "EASIX_ENABLE_GLOBAL_SEARCH", True),
        "SEARCH_MODELS": getattr(settings, "EASIX_SEARCH_MODELS", []),
        "DASHBOARD_WIDGETS": getattr(settings, "EASIX_DASHBOARD_WIDGETS", None),
        "SIDEBAR_NAVIGATION": getattr(settings, "EASIX_SIDEBAR_NAVIGATION", None),
        "THEME_COLOR": getattr(settings, "EASIX_THEME_COLOR", "indigo"),
        "ALLOW_REGISTRATION": getattr(settings, "EASIX_ALLOW_REGISTRATION", False),
    }
    
    def ready(self):
        """Initialize Easix when Django is ready."""
        from . import signals  # noqa: F401
        
        # Auto-register activity log signals if enabled
        if self.easix_settings["ENABLE_ACTIVITY_LOG"]:
            self._setup_activity_logging()
    
    def _setup_activity_logging(self):
        """Setup automatic activity logging for models."""
        from .activity.models import ActivityLog
        from .activity import signals as activity_signals  # noqa: F401
