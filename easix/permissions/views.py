"""
Permissions Views
User and role management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q

from ..views import get_easix_settings

User = get_user_model()


@staff_member_required
def permission_list(request):
    """List all permissions grouped by content type."""
    easix_settings = get_easix_settings()
    
    permissions = Permission.objects.all().select_related("content_type")
    
    # Group by content type
    grouped = {}
    for perm in permissions:
        ct = perm.content_type
        key = f"{ct.app_label}.{ct.model}"
        if key not in grouped:
            grouped[key] = {
                "name": f"{ct.app_label.title()} - {ct.model.title()}",
                "permissions": [],
            }
        grouped[key]["permissions"].append(perm)
    
    context = {
        "easix_settings": easix_settings,
        "grouped_permissions": grouped,
        "page_title": "Permissions",
    }
    
    return render(request, "easix/pages/permission_list.html", context)


@staff_member_required
def role_list(request):
    """List all roles (groups)."""
    easix_settings = get_easix_settings()
    roles = Group.objects.all().prefetch_related("permissions", "user_set")
    
    context = {
        "easix_settings": easix_settings,
        "roles": roles,
        "page_title": "Roles",
    }
    
    return render(request, "easix/pages/role_list.html", context)


@staff_member_required
def role_create(request):
    """Create a new role."""
    easix_settings = get_easix_settings()
    
    if request.method == "POST":
        name = request.POST.get("name")
        permissions = request.POST.getlist("permissions")
        
        if name:
            group = Group.objects.create(name=name)
            if permissions:
                group.permissions.set(permissions)
            
            messages.success(request, f"Role '{name}' created successfully.")
            return redirect("easix:role_list")
        else:
            messages.error(request, "Please provide a role name.")
    
    permissions = Permission.objects.all().select_related("content_type")
    
    context = {
        "easix_settings": easix_settings,
        "permissions": permissions,
        "page_title": "Create Role",
        "action": "create",
    }
    
    return render(request, "easix/pages/role_form.html", context)


@staff_member_required
def role_update(request, pk):
    """Update a role."""
    easix_settings = get_easix_settings()
    role = get_object_or_404(Group, pk=pk)
    
    if request.method == "POST":
        name = request.POST.get("name")
        permissions = request.POST.getlist("permissions")
        
        if name:
            role.name = name
            role.save()
            role.permissions.set(permissions)
            
            messages.success(request, f"Role '{name}' updated successfully.")
            return redirect("easix:role_list")
        else:
            messages.error(request, "Please provide a role name.")
    
    permissions = Permission.objects.all().select_related("content_type")
    
    context = {
        "easix_settings": easix_settings,
        "role": role,
        "permissions": permissions,
        "page_title": f"Edit Role: {role.name}",
        "action": "update",
    }
    
    return render(request, "easix/pages/role_form.html", context)


@staff_member_required
def user_list(request):
    """List all users."""
    easix_settings = get_easix_settings()
    
    query = request.GET.get("q", "")
    queryset = User.objects.all().prefetch_related("groups", "user_permissions")
    
    if query:
        queryset = queryset.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    users = queryset.order_by("-date_joined")
    
    context = {
        "easix_settings": easix_settings,
        "users": users,
        "page_title": "Users",
    }
    
    return render(request, "easix/pages/user_list.html", context)


@staff_member_required
def user_update(request, pk):
    """Update a user."""
    easix_settings = get_easix_settings()
    user = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        email = request.POST.get("email", "")
        is_active = request.POST.get("is_active") == "on"
        is_staff = request.POST.get("is_staff") == "on"
        groups = request.POST.getlist("groups")
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.is_active = is_active
        user.is_staff = is_staff
        user.groups.set(groups)
        user.save()
        
        messages.success(request, f"User '{user.username}' updated successfully.")
        return redirect("easix:user_list")
    
    groups = Group.objects.all()
    
    context = {
        "easix_settings": easix_settings,
        "user": user,
        "groups": groups,
        "page_title": f"Edit User: {user.username}",
    }
    
    return render(request, "easix/pages/user_form.html", context)
