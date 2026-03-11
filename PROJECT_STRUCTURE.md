# Easix Admin Framework

## Project Structure

```
easix-admin/
├── easix/                      # Main Easix package
│   ├── __init__.py
│   ├── apps.py                 # Django app configuration
│   ├── urls.py                 # URL routing
│   ├── views.py                # Main views
│   ├── signals.py              # Signal handlers
│   │
│   ├── dashboard/              # Dashboard module
│   │   ├── __init__.py
│   │   ├── widgets.py          # Widget classes
│   │   └── views.py            # Dashboard views
│   │
│   ├── tables/                 # Table module
│   │   ├── __init__.py
│   │   ├── config.py           # Table configuration
│   │   └── views.py            # Table views
│   │
│   ├── forms/                  # Forms module
│   │   ├── __init__.py
│   │   ├── config.py           # Form configuration
│   │   └── views.py            # Form views
│   │
│   ├── permissions/            # Permissions module
│   │   ├── __init__.py
│   │   └── views.py            # Permission views
│   │
│   ├── activity/               # Activity logging module
│   │   ├── __init__.py
│   │   ├── models.py           # ActivityLog model
│   │   ├── views.py            # Activity views
│   │   └── signals.py          # Activity signals
│   │
│   ├── components/             # UI components (Python)
│   │
│   ├── templates/
│   │   └── easix/
│   │       ├── base.html       # Base template
│   │       ├── components/     # Reusable components
│   │       ├── pages/          # Page templates
│   │       ├── partials/       # Partial templates
│   │       └── widgets/        # Widget templates
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── easix.css       # Main stylesheet
│   │   └── js/
│   │       └── easix.js        # Main JavaScript
│   │
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── easix_tags.py       # Template tags & filters
│   │
│   └── management/
│       └── commands/
│           └── easix.py        # CLI command
│
├── example/                    # Example project
│   ├── example/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── myapp/
│   │   ├── models.py           # Sample models
│   │   └── apps.py
│   ├── manage.py
│   └── README.md
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── test_easix.py
│
├── setup.py                    # Setup configuration
├── pyproject.toml              # Modern Python config
├── MANIFEST.in                 # Package manifest
├── README.md                   # Main documentation
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guide
└── LICENSE                     # MIT License
```

## Quick Start

### Installation
```bash
pip install easix-admin
```

### Configuration
```python
# settings.py
INSTALLED_APPS = [
    "easix",
]

# urls.py
urlpatterns = [
    path("admin/", include("easix.urls", namespace="easix")),
]
```

### Run Example
```bash
cd example
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit: http://localhost:8000/admin/

## Features

✅ Modern Dashboard with widgets
✅ Smart Table System (search, sort, filter, paginate)
✅ Responsive Design (desktop + mobile)
✅ Friendly Forms with field grouping
✅ Media Upload (drag-and-drop)
✅ Global Search across models
✅ Activity Log (audit trail)
✅ Permission Interface (roles & users)
✅ UI Components (button, card, modal, etc.)
✅ Zero-configuration setup

## Tech Stack

- **Backend**: Django 4.2+
- **Frontend**: Tailwind CSS, HTMX, Alpine.js
- **No React/Vue** - Server-driven UI

## Testing

```bash
pytest
```

## Documentation

See [README.md](README.md) for full documentation.

## License

MIT License - see [LICENSE](LICENSE)
