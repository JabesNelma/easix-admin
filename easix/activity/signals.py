"""
Activity Log Signals
Automatically log model changes.
"""
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import threading
import sys

# Thread-local storage for tracking changes
_thread_locals = threading.local()


def get_current_request():
    """Get current request from thread locals."""
    return getattr(_thread_locals, "request", None)


class ActivityMiddleware:
    """Middleware to store current request in thread locals."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        del _thread_locals.request
        return response


def _is_migrating():
    """Check if Django is currently running migrations."""
    return 'migrate' in sys.argv or 'makemigrations' in sys.argv


@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    """Log save operations."""
    # Skip during migrations
    if _is_migrating():
        return
    
    # Skip logging for certain models
    if sender._meta.app_label in ["admin", "sessions", "contenttypes", "easix"]:
        return
    
    # Skip if this is a signal for ActivityLog itself
    if sender.__name__ == "ActivityLog":
        return
    
    request = get_current_request()
    user = request.user if request and hasattr(request, "user") else None
    
    action = "created" if created else "updated"
    
    try:
        from .models import ActivityLog
        ActivityLog.objects.create(
            user=user,
            action=action,
            model_name=f"{sender._meta.app_label}.{sender._meta.model_name}",
            object_id=str(instance.pk),
            object_str=str(instance),
            ip_address=getattr(request, "META", {}).get("REMOTE_ADDR"),
            user_agent=getattr(request, "META", {}).get("HTTP_USER_AGENT", "")[:500] if request else "",
        )
    except Exception:
        pass  # Don't fail if logging fails


@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    """Log delete operations."""
    # Skip during migrations
    if _is_migrating():
        return
    
    # Skip logging for certain models
    if sender._meta.app_label in ["admin", "sessions", "contenttypes", "easix"]:
        return
    
    # Skip if this is a signal for ActivityLog itself
    if sender.__name__ == "ActivityLog":
        return
    
    request = get_current_request()
    user = request.user if request and hasattr(request, "user") else None
    
    try:
        from .models import ActivityLog
        ActivityLog.objects.create(
            user=user,
            action="deleted",
            model_name=f"{sender._meta.app_label}.{sender._meta.model_name}",
            object_id=str(instance.pk),
            object_str=str(instance),
            ip_address=getattr(request, "META", {}).get("REMOTE_ADDR"),
            user_agent=getattr(request, "META", {}).get("HTTP_USER_AGENT", "")[:500] if request else "",
        )
    except Exception:
        pass  # Don't fail if logging fails
