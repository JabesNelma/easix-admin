"""
Activity Log Views
"""
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.contrib import messages

from ..views import get_easix_settings
from .models import ActivityLog


@staff_member_required
def activity_log(request):
    """View activity log."""
    easix_settings = get_easix_settings()
    
    # Get filters
    query = request.GET.get("q", "")
    action = request.GET.get("action", "")
    user_id = request.GET.get("user", "")
    
    # Build queryset
    queryset = ActivityLog.objects.all().select_related("user")
    
    if query:
        queryset = queryset.filter(
            models.Q(object_str__icontains=query) |
            models.Q(model_name__icontains=query) |
            models.Q(user__username__icontains=query)
        )
    
    if action:
        queryset = queryset.filter(action=action)
    
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    
    # Pagination
    paginator = Paginator(queryset, 50)
    page_number = request.GET.get("page", 1)
    activities = paginator.get_page(page_number)
    
    # Get users for filter
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.all()[:100]
    
    context = {
        "easix_settings": easix_settings,
        "activities": activities,
        "users": users,
        "page_title": "Activity Log",
    }
    
    return render(request, "easix/pages/activity_log.html", context)


@staff_member_required
def clear_activity(request):
    """Clear all activity logs."""
    if request.method == "POST":
        ActivityLog.objects.all().delete()
        messages.success(request, "All activity logs have been cleared.")
    
    return redirect("easix:activity_log")
