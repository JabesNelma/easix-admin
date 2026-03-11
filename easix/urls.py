"""
Easix Admin URL Configuration
"""
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .dashboard import views as dashboard_views
from .tables import views as tables_views
from .forms import views as forms_views
from .permissions import views as permissions_views
from .activity import views as activity_views

app_name = "easix"

urlpatterns = [
    # Authentication
    path("login/", auth_views.LoginView.as_view(template_name="easix/pages/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    
    # Dashboard
    path("", dashboard_views.dashboard, name="dashboard"),
    
    # Model list and CRUD
    path("models/<str:app_label>/<str:model_name>/", tables_views.model_list, name="model_list"),
    path("models/<str:app_label>/<str:model_name>/create/", forms_views.model_create, name="model_create"),
    path("models/<str:app_label>/<str:model_name>/<int:pk>/", forms_views.model_detail, name="model_detail"),
    path("models/<str:app_label>/<str:model_name>/<int:pk>/edit/", forms_views.model_update, name="model_update"),
    path("models/<str:app_label>/<str:model_name>/<int:pk>/delete/", forms_views.model_delete, name="model_delete"),
    path("models/<str:app_label>/<str:model_name>/<int:pk>/duplicate/", forms_views.model_duplicate, name="model_duplicate"),
    
    # Table actions
    path("tables/<str:app_label>/<str:model_name>/data/", tables_views.table_data, name="table_data"),
    path("tables/<str:app_label>/<str:model_name>/bulk-action/", tables_views.bulk_action, name="bulk_action"),
    path("tables/<str:app_label>/<str:model_name>/export/", tables_views.export_csv, name="export_csv"),
    
    # Global search
    path("search/", views.global_search, name="global_search"),
    path("search/models/", views.search_models, name="search_models"),
    
    # Activity log
    path("activity/", activity_views.activity_log, name="activity_log"),
    path("activity/clear/", activity_views.clear_activity, name="clear_activity"),
    
    # Permissions and roles
    path("permissions/", permissions_views.permission_list, name="permission_list"),
    path("permissions/roles/", permissions_views.role_list, name="role_list"),
    path("permissions/roles/create/", permissions_views.role_create, name="role_create"),
    path("permissions/roles/<int:pk>/edit/", permissions_views.role_update, name="role_update"),
    path("permissions/users/", permissions_views.user_list, name="user_list"),
    path("permissions/users/<int:pk>/edit/", permissions_views.user_update, name="user_update"),
    
    # File upload
    path("upload/", views.file_upload, name="file_upload"),
    
    # Settings
    path("settings/", views.settings_view, name="settings"),
]
