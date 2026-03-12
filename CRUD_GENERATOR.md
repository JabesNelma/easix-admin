# Easix Admin - CRUD Generator Documentation

Complete guide to using the Easix CRUD Generator for building admin interfaces with minimal configuration.

## Table of Contents

1. [Quick Start](#quick-start)
2. [List View](#list-view)
3. [Create/Edit Form](#createedit-form)
4. [Detail View](#detail-view)
5. [Components](#components)
6. [Customization](#customization)

---

## Quick Start

### Minimal Setup (3 Lines!)

```python
# app.py
from easix import EasixAdmin
from myapp.models import User, Post, Product

admin = EasixAdmin(app)
admin.register(User)
admin.register(Post)
admin.register(Product)
```

That's it! Easix automatically generates:
- ✅ List view with search, filter, sort, pagination
- ✅ Create/Edit forms with validation
- ✅ Detail view with readonly fields
- ✅ Delete confirmation
- ✅ Mobile-responsive design
- ✅ Dark mode support

---

## List View

### Features

| Feature | Description |
|---------|-------------|
| **Search** | Debounced search across all fields |
| **Filter** | Dropdown filters for choices/foreign keys |
| **Sort** | Click column headers to sort |
| **Pagination** | Configurable page sizes |
| **Bulk Actions** | Select multiple items for actions |
| **Export** | CSV/Excel export buttons |
| **Mobile Card View** | Automatic card layout on mobile |

### Template

```html
<!-- templates/easix/pages/model_list.html -->
{% extends "easix/base.html" %}
{% load easix_tags %}

{% block content %}
<div x-data="crudList({
    modelUrl: '{{ model.app_label }}/{{ model.model_name }}',
    listUrl: '{% url "easix:model_list" model.app_label model.model_name %}',
    createUrl: '{% url "easix:model_create" model.app_label model.model_name %}',
    dataUrl: '{% url "easix:model_list_api" model.app_label model.model_name %}',
    perPage: 25,
    columns: {{ columns|safe }},
    filters: {{ filters|safe }}
})">

    {# Search & Filters #}
    {% include "easix/components/search_input.html" %}
    
    {# Data Table #}
    <div x-show="!loading && data.length > 0">
        <table class="table">
            <!-- Headers with sorting -->
            <thead>
                <tr>
                    <th>Select All</th>
                    {% for col in columns %}
                    <th @click="toggleSort('{{ col.field }}')">{{ col.label }}</th>
                    {% endfor %}
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for item in data %}
                <tr>
                    <td><input type="checkbox" x-model="selectedRows"></td>
                    {% for col in columns %}
                    <td>{{ item|get_item:col.field }}</td>
                    {% endfor %}
                    <td>
                        <a href="{{ item.pk }}/view/">View</a>
                        <a href="{{ item.pk }}/change/">Edit</a>
                        <button @click="confirmDelete(item)">Delete</button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    {# Pagination #}
    {% include "easix/components/pagination.html" %}
</div>
{% endblock %}
```

### Column Configuration

```python
columns = [
    {
        'field': 'title',
        'label': 'Title',
        'sortable': True,
        'searchable': True,
        'visible': True,
        'type': 'text'
    },
    {
        'field': 'status',
        'label': 'Status',
        'sortable': True,
        'filterable': True,
        'type': 'badge',
        'badge_map': {
            'published': {'style': 'success', 'label': 'Published'},
            'draft': {'style': 'warning', 'label': 'Draft'},
            'archived': {'style': 'danger', 'label': 'Archived'}
        }
    },
    {
        'field': 'author',
        'label': 'Author',
        'type': 'relation',
        'relation_model': 'auth.User'
    },
    {
        'field': 'created_at',
        'label': 'Created At',
        'type': 'datetime',
        'sortable': True
    }
]
```

### Filter Configuration

```python
filters = [
    {
        'field': 'status',
        'label': 'Status',
        'type': 'select',
        'options': [
            {'value': 'published', 'label': 'Published'},
            {'value': 'draft', 'label': 'Draft'},
            {'value': 'archived', 'label': 'Archived'}
        ]
    },
    {
        'field': 'category',
        'label': 'Category',
        'type': 'select',
        'options': Category.objects.all().values('id', 'name')
    }
]
```

---

## Create/Edit Form

### Features

| Feature | Description |
|---------|-------------|
| **Auto Fields** | Automatically detects field types |
| **Validation** | Client-side and server-side validation |
| **Fieldsets** | Group fields into tabs/sections |
| **Unsaved Warning** | Warns before leaving with unsaved changes |
| **File Upload** | Drag-drop file upload with preview |
| **Relation Fields** | Searchable dropdown for foreign keys |

### Template

```html
<!-- templates/easix/pages/model_form.html -->
{% extends "easix/base.html" %}

{% block content %}
<div x-data="crudForm({
    submitUrl: '{{ submit_url }}',
    model: '{{ model.app_label }}.{{ model.model_name }}'
})">

    <form method="post" @submit.prevent="submit" enctype="multipart/form-data">
        {% csrf_token %}
        
        {# Fieldsets (Optional) #}
        {% if fieldsets %}
        <div x-data="tabs()">
            {# Tab Headers #}
            {% for fieldset in fieldsets %}
            <button @click="select({{ forloop.counter0 }})">
                {{ fieldset.title }}
            </button>
            {% endfor %}
            
            {# Tab Panels #}
            {% for fieldset in fieldsets %}
            <div x-show="isActive({{ forloop.counter0 }})">
                {% for field_name in fieldset.fields %}
                {% include "easix/components/form_field.html" %}
                {% endfor %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {# Simple Form (no fieldsets) #}
        {% for field in form.visible_fields %}
        {% include "easix/components/form_field.html" %}
        {% endfor %}
        
        {# Actions #}
        <button type="submit" :disabled="submitting">
            <span x-show="!submitting">Save</span>
            <span x-show="submitting">Saving...</span>
        </button>
    </form>
</div>
{% endblock %}
```

### Field Configuration

```python
from easix.tables import FormConfig, Fieldset

form_config = FormConfig(
    fieldsets=[
        Fieldset(
            title='Basic Information',
            icon='document-text',
            description='Core information about this item',
            fields=['title', 'slug', 'description', 'status']
        ),
        Fieldset(
            title='Content',
            icon='pencil',
            fields=['content', 'excerpt']
        ),
        Fieldset(
            title='Media',
            icon='photograph',
            fields=['image', 'attachments']
        ),
        Fieldset(
            title='Settings',
            icon='cog',
            fields=['is_featured', 'publish_date', 'author']
        )
    ],
    submit_label='Save Item'
)
```

### Field Types

| Type | Widget | Description |
|------|--------|-------------|
| `text` | Text input | Default text field |
| `textarea` | Textarea | Multi-line text |
| `select` | Dropdown | Choice field |
| `checkbox` | Checkbox | Boolean field |
| `radio` | Radio buttons | Single choice |
| `date` | Date picker | Date field |
| `datetime` | DateTime picker | Date and time |
| `number` | Number input | Numeric field |
| `email` | Email input | Email validation |
| `url` | URL input | Website URL |
| `password` | Password input | Hidden text |
| `file` | File upload | File input |
| `image` | Image upload | Image with preview |
| `relation` | Search dropdown | Foreign key |

---

## Detail View

### Features

| Feature | Description |
|---------|-------------|
| **Readonly Display** | All fields displayed nicely |
| **Field Grouping** | Organized in tabs/sections |
| **Smart Formatting** | Dates, booleans, files formatted |
| **Related Objects** | Shows related items |
| **Metadata** | Created/updated timestamps |

### Template

```html
<!-- templates/easix/pages/model_detail.html -->
{% extends "easix/base.html" %}

{% block content %}
<div class="max-w-4xl mx-auto">
    {# Header with Actions #}
    <div class="flex justify-between">
        <h1>{{ object }}</h1>
        <div>
            <a href="change/" class="btn btn-primary">Edit</a>
            <button @click="showDeleteModal = true" class="btn btn-danger">Delete</button>
        </div>
    </div>
    
    {# Detail Cards #}
    {% if fieldsets %}
    <div x-data="tabs()">
        {% for fieldset in fieldsets %}
        <div x-show="isActive({{ forloop.counter0 }})">
            <dl class="grid grid-cols-2 gap-4">
                {% for field_name in fieldset.fields %}
                <div>
                    <dt>{{ field_name|title }}</dt>
                    <dd>{{ object|get_field_value:field_name }}</dd>
                </div>
                {% endfor %}
            </dl>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    {# Metadata #}
    <div class="card">
        <h3>Metadata</h3>
        <dl>
            <dt>Created</dt>
            <dd>{{ created_at|date:"M d, Y H:i" }}</dd>
            <dt>Updated</dt>
            <dd>{{ updated_at|date:"M d, Y H:i" }}</dd>
            <dt>Created By</dt>
            <dd>{{ created_by }}</dd>
        </dl>
    </div>
</div>
{% endblock %}
```

---

## Components

### Search Input

```html
{% include "easix/components/search_input.html" with 
    name='search'
    placeholder='Search items...'
    debounce_ms=300
    auto_submit=False
    show_loading=True
    class='w-full max-w-md'
%}
```

### Pagination

```html
{% include "easix/components/pagination.html" with 
    pagination=page_obj
    query_params='?status=published'
%}
```

### Form Field

```html
{% include "easix/components/form_field.html" with 
    field=form.title
    field_type='text'
    value=form.title.value
    errors=form.title.errors
    show_label=True
    help_text='Enter a descriptive title'
    placeholder='Enter title...'
    required=True
%}
```

---

## Customization

### Override Templates

1. Create folder in your project:
```
myproject/
├── templates/
│   └── easix/
│       ├── pages/
│       │   ├── model_list.html
│       │   ├── model_form.html
│       │   └── model_detail.html
│       └── components/
```

2. Easix automatically uses your templates instead of defaults!

### Custom CSS

```python
admin = EasixAdmin(app, custom_css='static/my_admin.css')
```

```css
/* static/my_admin.css */
:root {
    --easix-primary: #10B981;  /* Green instead of blue */
}

.card {
    border-radius: 16px;  /* More rounded */
}
```

### Custom JavaScript

```python
admin = EasixAdmin(app, custom_js='static/my_admin.js')
```

```javascript
// static/my_admin.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Easix Admin customized!');
    
    // Add custom behavior
    window.addEventListener('toast', (e) => {
        console.log('Toast:', e.detail.message);
    });
});
```

---

## API Endpoints

### List API

```
GET /admin/models/{app_label}/{model_name}/api/

Query Parameters:
- page: Page number (default: 1)
- per_page: Items per page (default: 25)
- sort: Sort field (prefix with - for desc)
- search: Search query
- filter_{field}: Filter by field

Response:
{
    "results": [...],
    "count": 100,
    "page": 1,
    "total_pages": 4,
    "columns": [...],
    "filters": [...],
    "bulkActions": [...]
}
```

### Create API

```
POST /admin/models/{app_label}/{model_name}/api/create/

Body: FormData with field values

Response:
{
    "success": true,
    "id": 123,
    "url": "/admin/models/app/model/123/"
}
```

### Update API

```
PUT /admin/models/{app_label}/{model_name}/api/{id}/update/

Response:
{
    "success": true,
    "message": "Updated successfully"
}
```

### Delete API

```
POST /admin/models/{app_label}/{model_name}/api/{id}/delete/

Response:
{
    "success": true,
    "message": "Deleted successfully"
}
```

---

## Examples

### Product Model

```python
# models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

# admin.py
from easix import EasixAdmin
from easix.tables import TableConfig, Column, Filter
from easix.forms import FormConfig, Fieldset

admin = EasixAdmin(app)

@admin.register(Product)
class ProductAdmin:
    table_config = TableConfig(
        columns=[
            Column('name', 'Product Name', sortable=True, searchable=True),
            Column('price', 'Price', type='currency'),
            Column('category', 'Category', type='relation'),
            Column('is_active', 'Active', type='boolean'),
            Column('created_at', 'Created', type='datetime')
        ],
        filters=[
            Filter('category', 'Category', type='select'),
            Filter('is_active', 'Status', type='boolean')
        ]
    )
    
    form_config = FormConfig(
        fieldsets=[
            Fieldset('Basic Info', fields=['name', 'price', 'category']),
            Fieldset('Description', fields=['description']),
            Fieldset('Media', fields=['image']),
            Fieldset('Settings', fields=['is_active'])
        ]
    )
```

---

## Support

- **Documentation**: https://easix.dev/docs
- **Issues**: https://github.com/easix-admin/easix/issues
- **Discussions**: https://github.com/easix-admin/easix/discussions

Built with ❤️ for the Django community.
