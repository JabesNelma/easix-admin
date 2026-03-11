"""
Easix Signals
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save)
@receiver(post_delete)
def log_model_changes(sender, instance, **kwargs):
    """Log model changes for activity tracking."""
    # This is handled by the activity app
    pass
