"""
Tests for Easix framework.
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class TestEasixConfig(TestCase):
    """Test Easix configuration."""
    
    def test_app_config(self):
        """Test that Easix app is properly configured."""
        from django.apps import apps
        easix_config = apps.get_app_config("easix")
        self.assertEqual(easix_config.name, "easix")
        self.assertEqual(easix_config.verbose_name, "Easix Admin")
    
    def test_settings_loaded(self):
        """Test that Easix settings are loaded."""
        from django.conf import settings
        self.assertTrue(hasattr(settings, "EASIX_SITE_TITLE"))
        self.assertTrue(hasattr(settings, "EASIX_ENABLE_ACTIVITY_LOG"))


class TestDashboardViews(TestCase):
    """Test dashboard views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="password123"
        )
        self.client.login(username="admin", password="password123")
    
    def test_dashboard_accessible(self):
        """Test that dashboard is accessible."""
        response = self.client.get(reverse("easix:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires login."""
        self.client.logout()
        response = self.client.get(reverse("easix:dashboard"))
        self.assertNotEqual(response.status_code, 200)


class TestTableConfig(TestCase):
    """Test table configuration."""
    
    def test_column_creation(self):
        """Test Column dataclass creation."""
        from easix.tables import Column
        
        col = Column(field="name", label="Name")
        self.assertEqual(col.field, "name")
        self.assertEqual(col.label, "Name")
        self.assertTrue(col.sortable)
    
    def test_action_creation(self):
        """Test Action dataclass creation."""
        from easix.tables import Action
        
        action = Action(label="Edit", icon="pencil", url_pattern="edit")
        self.assertEqual(action.label, "Edit")
        self.assertEqual(action.icon, "pencil")
    
    def test_filter_creation(self):
        """Test Filter dataclass creation."""
        from easix.tables import Filter
        
        filter_obj = Filter(
            field="status",
            label="Status",
            type="select",
            options=[{"value": "active", "label": "Active"}]
        )
        self.assertEqual(filter_obj.field, "status")
        self.assertEqual(len(filter_obj.options), 1)


class TestFormConfig(TestCase):
    """Test form configuration."""
    
    def test_fieldset_creation(self):
        """Test Fieldset dataclass creation."""
        from easix.forms import Fieldset
        
        fieldset = Fieldset(
            title="Basic Info",
            fields=["name", "email"]
        )
        self.assertEqual(fieldset.title, "Basic Info")
        self.assertEqual(len(fieldset.fields), 2)
    
    def test_form_field_creation(self):
        """Test FormField dataclass creation."""
        from easix.forms import FormField
        
        field = FormField(
            name="email",
            label="Email Address",
            type="email",
            required=True
        )
        self.assertEqual(field.name, "email")
        self.assertEqual(field.type, "email")
        self.assertTrue(field.is_required(None))


class TestActivityLog(TestCase):
    """Test activity logging."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="password123"
        )
    
    def test_activity_log_creation(self):
        """Test creating activity log entries."""
        from easix.activity.models import ActivityLog
        
        log = ActivityLog.objects.create(
            user=self.user,
            action="created",
            model_name="myapp.Product",
            object_id="1",
            object_str="Test Product"
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, "created")
        self.assertEqual(str(log), "testuser created myapp.Product (1)")
    
    def test_activity_log_manager(self):
        """Test ActivityLog manager methods."""
        from easix.activity.models import ActivityLog
        
        ActivityLog.objects.create(
            user=self.user,
            action="updated",
            model_name="myapp.Order",
            object_id="2"
        )
        
        logs = ActivityLog.objects.get_by_user(self.user)
        self.assertEqual(logs.count(), 1)
        
        logs = ActivityLog.objects.get_by_action("updated")
        self.assertEqual(logs.count(), 1)


class TestTemplateTags(TestCase):
    """Test template tags."""
    
    def test_icon_filter(self):
        """Test icon template filter."""
        from easix.templatetags.easix_tags import icon
        
        result = icon("dashboard")
        self.assertIn("svg", result)
        self.assertIn("dashboard", result)
    
    def test_badge_class_filter(self):
        """Test badge class template filter."""
        from easix.templatetags.easix_tags import badge_class
        
        self.assertEqual(badge_class(True), "success")
        self.assertEqual(badge_class(False), "danger")
        self.assertEqual(badge_class("active"), "success")
    
    def test_format_value_filter(self):
        """Test format value template filter."""
        from easix.templatetags.easix_tags import format_value
        
        self.assertEqual(format_value(1234.5, "currency"), "$1,234.50")
        self.assertEqual(format_value(True, "boolean"), "Yes")
        self.assertEqual(format_value(False, "boolean"), "No")


class TestWidgets(TestCase):
    """Test dashboard widgets."""
    
    def test_stat_widget(self):
        """Test StatWidget."""
        from easix.dashboard.widgets import StatWidget
        
        widget = StatWidget(
            title="Total Users",
            value=100,
            icon="users",
            trend=10.5
        )
        
        context = widget.get_context(None)
        self.assertEqual(context["title"], "Total Users")
        self.assertEqual(context["value"], 100)
        self.assertEqual(context["trend"], 10.5)
    
    def test_model_count_widget(self):
        """Test ModelCountWidget."""
        from easix.dashboard.widgets import ModelCountWidget
        
        widget = ModelCountWidget(
            model="auth.User",
            icon="users"
        )
        
        # Widget should handle non-existent model gracefully
        context = widget.get_context(None)
        self.assertIn("value", context)


@pytest.mark.django_db
def test_global_search():
    """Test global search functionality."""
    from django.test import Client
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    client = Client()
    
    # Create test user
    User.objects.create_user(
        username="searchtest",
        email="search@test.com",
        password="password"
    )
    
    # Login
    client.login(username="searchtest", password="password")
    
    # Test search
    response = client.get(reverse("easix:global_search"), {"q": "search"})
    assert response.status_code == 200


@pytest.mark.django_db
def test_model_list_view():
    """Test model list view."""
    from django.test import Client
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    client = Client()
    
    # Create superuser
    User.objects.create_superuser(
        username="listtest",
        email="list@test.com",
        password="password"
    )
    
    # Login
    client.login(username="listtest", password="password")
    
    # Test user list
    response = client.get(reverse("easix:model_list", args=["auth", "user"]))
    assert response.status_code == 200
