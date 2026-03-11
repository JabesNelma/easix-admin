# Easix Example Project

This example project demonstrates the Easix Django admin framework with sample models.

## Quick Start

```bash
# Navigate to example directory
cd example

# Install dependencies
pip install -e ..

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Then visit: http://localhost:8000/admin/

## Sample Models

The example includes three models to demonstrate Easix features:

### Customer
- Basic contact information
- Company details
- Timestamps

### Product
- Product information with description
- Pricing and inventory
- Status (Draft, Active, Archived)
- Image upload

### Order
- Order tracking with unique order numbers
- Customer and product relationships
- Status workflow (Pending → Processing → Shipped → Delivered)
- Automatic total calculation

## Features Demonstrated

1. **Dashboard Widgets** - Stats, recent items, quick actions, activity
2. **Smart Tables** - Search, sort, filter, pagination, bulk actions
3. **Responsive Design** - Mobile card layout for tables
4. **Friendly Forms** - Grouped fieldsets with clear labels
5. **Activity Logging** - Automatic audit trail
6. **Global Search** - Search across all models
7. **Permission Management** - Roles and users interface

## Login

Use the superuser credentials you created with `createsuperuser`.
