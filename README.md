# Easix Admin Framework

**A modern, user-friendly Django admin framework designed for non-technical users.**

[![PyPI version](https://badge.fury.io/py/easix-admin.svg)](https://badge.fury.io/py/easix-admin)
[![Django versions](https://img.shields.io/badge/Django-4.2%2B-green.svg)](https://www.djangoproject.com/)
[![Python versions](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Quick Start

### Installation

```bash
pip install easix-admin
```

### Configuration

Add `easix` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... your apps
    "easix",  # Add this
]
```

Add the URL configuration to your `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path("admin/", include("easix.urls", namespace="easix")),
    # ... your other URLs
]
```

That's it! Easix will automatically transform your Django admin experience.

---

## ✨ Features

### 🎯 Core Features

- **Modern Dashboard** - Configurable widgets showing stats, charts, and recent activity
- **Smart Table System** - Search, sort, filter, paginate, and bulk actions
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Friendly Forms** - Auto-grouped fields with clear labels and helpful descriptions
- **Media Upload** - Drag-and-drop file uploads with preview
- **Global Search** - Search across all your models from anywhere
- **Activity Log** - Automatic audit trail of all user actions
- **Permission Management** - Visual role and permission interface

### 🛠️ Technology Stack

- **Backend**: Django 4.2+
- **Frontend**: Tailwind CSS, HTMX, Alpine.js
- **No React/Vue** - Server-driven, lightweight UI

---

## 📖 Documentation

### Configuration Options

Add these to your `settings.py` to customize Easix:

```python
# Site branding
EASIX_SITE_TITLE = "My Admin Dashboard"
EASIX_SITE_BRAND = "MyApp"
EASIX_SITE_LOGO = "/static/logo.png"

# Features
EASIX_ENABLE_ACTIVITY_LOG = True
EASIX_ENABLE_GLOBAL_SEARCH = True

# Pagination
EASIX_DASHBOARD_PER_PAGE = 10
EASIX_TABLE_PER_PAGE = 25

# Theme
EASIX_THEME_COLOR = "indigo"  # indigo, blue, green, red, etc.

# Models to search
EASIX_SEARCH_MODELS = [
    "myapp.Product",
    "myapp.Order",
    "auth.User",
]

# Custom dashboard widgets
EASIX_DASHBOARD_WIDGETS = [
    {"widget": "easix.dashboard.widgets.ModelCountWidget", "args": {"model": "myapp.Product"}},
    {"widget": "easix.dashboard.widgets.RecentItemsWidget", "args": {"model": "myapp.Order", "limit": 5}},
]
```

### Model Configuration

Configure how your models appear in Easix:

```python
from easix.tables import TableConfig, Column, Action, Filter
from easix.forms import FormConfig, Fieldset

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("draft", "Draft")])
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
    
    # Table configuration
    easix_table_config = TableConfig(
        columns=[
            Column(field="name", label="Product Name", sortable=True, searchable=True),
            Column(field="price", label="Price", type="number", format=lambda v: f"${v}"),
            Column(field="status", label="Status", badge={"active": "success", "draft": "warning"}),
        ],
        actions=[
            Action(label="View", icon="eye", url_pattern="easix:model_detail"),
            Action(label="Edit", icon="pencil", url_pattern="easix:model_update"),
        ],
        bulk_actions=[
            BulkAction(label="Delete Selected", icon="trash", action_name="delete_selected"),
        ],
        filters=[
            Filter(field="status", label="Status", type="select", options=[
                {"value": "active", "label": "Active"},
                {"value": "draft", "label": "Draft"},
            ]),
        ],
    )
    
    # Form configuration
    easix_form_config = FormConfig(
        fieldsets=[
            Fieldset(
                title="Basic Information",
                icon="information-circle",
                fields=["name", "price", "status"],
            ),
            Fieldset(
                title="Media",
                icon="photograph",
                fields=["image"],
            ),
        ],
        submit_label="Save Product",
    )
```

### Custom Dashboard Widgets

Create custom widgets for your dashboard:

```python
from easix.dashboard.widgets import StatWidget, Widget

class RevenueWidget(StatWidget):
    def __init__(self):
        super().__init__(
            title="Total Revenue",
            value="$0",  # Calculate dynamically
            icon="currency-dollar",
            trend=12.5,  # Percentage increase
        )
    
    def get_context(self, request):
        context = super().get_context(request)
        # Calculate actual revenue
        from myapp.models import Order
        revenue = Order.objects.aggregate(total=models.Sum("total"))["total"] or 0
        context["value"] = f"${revenue:,.2f}"
        return context

# Add to settings
EASIX_DASHBOARD_WIDGETS = [
    {"widget": "myapp.widgets.RevenueWidget", "args": {}},
]
```

---

## 🎨 UI Components

Easix includes reusable UI components:

### Buttons

```html
{% include "easix/components/button.html" with style='primary' label='Save' icon='check' %}
{% include "easix/components/button.html" with style='danger' label='Delete' icon='trash' %}
```

### Cards

```html
{% include "easix/components/card.html" with title='Users' icon='users' %}
```

### Badges

```html
{% include "easix/components/badge.html" with value='Active' style='success' %}
```

### Alerts

```html
{% include "easix/components/alert.html" with style='success' message='Saved successfully!' %}
```

---

## 📱 Mobile Support

Easix is mobile-first:

- **Responsive Tables** - Tables transform to cards on mobile
- **Collapsible Sidebar** - Hamburger menu on small screens
- **Touch-Friendly** - Large tap targets and smooth interactions

---

## 🔒 Permissions

Easix uses Django's built-in permission system:

1. Go to **Permissions → Roles**
2. Create roles like "Admin", "Editor", "Viewer"
3. Assign permissions to each role
4. Assign users to roles

---

## 📊 Activity Log

All actions are automatically logged:

- User created/updated/deleted records
- Timestamp and IP address tracking
- Filterable and searchable log

---

## 🧪 Testing

Run tests:

```bash
pytest
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/JabesNelma/easix-admin.git
cd easix-admin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

---

## 📄 License

Easix is released under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

Easix is inspired by:
- [Filament](https://filamentphp.com/) - Laravel admin framework
- [Laravel Nova](https://nova.laravel.com/) - Laravel admin panel
- [Django Jazzmin](https://django-jazzmin.readthedocs.io/) - Django admin theme

---

## 📞 Support

- **Documentation**: https://easix.dev/docs
- **Issues**: https://github.com/JabesNelma/easix-admin/issues
- **Discussions**: https://github.com/JabesNelma/easix-admin/discussions

---

Built with ❤️ for the Django community.
