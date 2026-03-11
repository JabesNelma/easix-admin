"""
Activity Log Models
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class ActivityLogManager(models.Manager):
    """Custom manager for ActivityLog."""
    
    def log_action(self, user, action, model_name, object_id, object_str="", extra=None, ip_address=None):
        """Create a new activity log entry."""
        return self.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id),
            object_str=object_str,
            extra=extra or {},
            ip_address=ip_address,
        )
    
    def get_by_user(self, user):
        """Get all activities by a specific user."""
        return self.filter(user=user)
    
    def get_by_model(self, model_name):
        """Get all activities for a specific model."""
        return self.filter(model_name=model_name)
    
    def get_by_action(self, action):
        """Get all activities with a specific action."""
        return self.filter(action=action)
    
    def recent(self, days=7):
        """Get recent activities."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(timestamp__gte=cutoff)
    
    def clear_old(self, days=90):
        """Clear activities older than specified days."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(timestamp__lt=cutoff).delete()


class ActivityLog(models.Model):
    """
    Activity log for tracking user actions.
    
    This model automatically logs all create, update, and delete operations
    on registered models for audit and debugging purposes.
    """
    
    ACTIONS = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("deleted", "Deleted"),
        ("viewed", "Viewed"),
        ("duplicated", "Duplicated"),
        ("imported", "Imported"),
        ("exported", "Exported"),
        ("published", "Published"),
        ("unpublished", "Unpublished"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("other", "Other"),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activity_logs",
        help_text="User who performed the action",
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTIONS,
        help_text="Type of action performed",
    )
    
    model_name = models.CharField(
        max_length=255,
        help_text="Full model name (app.Model)",
        db_index=True,
    )
    
    object_id = models.CharField(
        max_length=255,
        help_text="Primary key of the affected object",
        db_index=True,
    )
    
    object_str = models.CharField(
        max_length=500,
        blank=True,
        help_text="String representation of the object",
    )
    
    extra = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data about the action",
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the request",
    )
    
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        help_text="User agent string",
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action occurred",
        db_index=True,
    )
    
    objects = ActivityLogManager()
    
    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["model_name", "object_id"]),
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["action"]),
        ]
    
    def __str__(self):
        user_str = self.user.get_username() if self.user else "System"
        return f"{user_str} {self.action} {self.model_name} ({self.object_id})"
    
    def get_action_icon(self):
        """Get icon for action type."""
        icons = {
            "created": "plus",
            "updated": "pencil",
            "deleted": "trash",
            "viewed": "eye",
            "duplicated": "duplicate",
            "published": "check",
            "unpublished": "x-mark",
        }
        return icons.get(self.action, "activity")
    
    def get_action_color(self):
        """Get color class for action type."""
        colors = {
            "created": "green",
            "updated": "blue",
            "deleted": "red",
            "published": "green",
            "unpublished": "yellow",
        }
        return colors.get(self.action, "gray")
