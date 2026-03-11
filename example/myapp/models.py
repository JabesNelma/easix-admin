"""
Example Django App for Easix Demo
Demonstrates Easix features with Product, Order, and Customer models.
"""
from django.db import models
from django.urls import reverse
from easix.tables import TableConfig, Column, Action, Filter, BulkAction
from easix.forms import FormConfig, Fieldset


class Customer(models.Model):
    """Customer model for demo."""
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse("easix:model_detail", args=["myapp", "customer", self.pk])

    # Table configuration
    easix_table_config = TableConfig(
        columns=[
            Column(field="first_name", label="First Name", sortable=True, searchable=True),
            Column(field="last_name", label="Last Name", sortable=True, searchable=True),
            Column(field="email", label="Email", type="email"),
            Column(field="company", label="Company"),
            Column(field="created_at", label="Created", type="datetime"),
        ],
        mobile_display=["first_name", "last_name", "email"],
    )
    
    # Form configuration
    easix_form_config = FormConfig(
        fieldsets=[
            Fieldset(
                title="Personal Information",
                icon="user",
                fields=["first_name", "last_name", "email", "phone"],
            ),
            Fieldset(
                title="Company Information",
                icon="building",
                fields=["company"],
            ),
        ],
        submit_label="Save Customer",
    )


class Product(models.Model):
    """Product model for demo."""
    
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("archived", "Archived"),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("easix:model_detail", args=["myapp", "product", self.pk])
    
    # Table configuration
    easix_table_config = TableConfig(
        columns=[
            Column(field="name", label="Product Name", sortable=True, searchable=True),
            Column(field="category", label="Category", sortable=True),
            Column(field="price", label="Price", type="number", format=lambda v: f"${v}"),
            Column(field="stock", label="Stock", type="number"),
            Column(
                field="status", 
                label="Status", 
                badge={"active": "success", "draft": "warning", "archived": "danger"}
            ),
            Column(field="created_at", label="Created", type="datetime"),
        ],
        filters=[
            Filter(
                field="status",
                label="Status",
                type="select",
                options=[
                    {"value": "active", "label": "Active"},
                    {"value": "draft", "label": "Draft"},
                    {"value": "archived", "label": "Archived"},
                ],
            ),
            Filter(
                field="category",
                label="Category",
                type="select",
                options=[],  # Would be populated dynamically
            ),
        ],
        mobile_display=["name", "price", "status"],
    )
    
    # Form configuration
    easix_form_config = FormConfig(
        fieldsets=[
            Fieldset(
                title="Basic Information",
                icon="information-circle",
                fields=["name", "description", "category"],
            ),
            Fieldset(
                title="Pricing & Inventory",
                icon="currency-dollar",
                fields=["price", "stock"],
            ),
            Fieldset(
                title="Status",
                icon="check-circle",
                fields=["status"],
            ),
            Fieldset(
                title="Media",
                icon="photograph",
                fields=["image"],
            ),
        ],
        submit_label="Save Product",
    )


class Order(models.Model):
    """Order model for demo."""
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            self.order_number = f"ORD-{random.randint(10000, 99999)}"
        if self.product and self.quantity:
            self.total = self.product.price * self.quantity
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("easix:model_detail", args=["myapp", "order", self.pk])
    
    # Table configuration
    easix_table_config = TableConfig(
        columns=[
            Column(field="order_number", label="Order #", sortable=True, searchable=True),
            Column(field="customer", label="Customer", format=lambda v: str(v)),
            Column(field="product", label="Product", format=lambda v: str(v)),
            Column(field="quantity", label="Qty", type="number"),
            Column(field="total", label="Total", type="number", format=lambda v: f"${v}"),
            Column(
                field="status",
                label="Status",
                badge={
                    "pending": "warning",
                    "processing": "info",
                    "shipped": "primary",
                    "delivered": "success",
                    "cancelled": "danger",
                },
            ),
            Column(field="created_at", label="Date", type="date"),
        ],
        filters=[
            Filter(
                field="status",
                label="Status",
                type="select",
                options=[
                    {"value": "pending", "label": "Pending"},
                    {"value": "processing", "label": "Processing"},
                    {"value": "shipped", "label": "Shipped"},
                    {"value": "delivered", "label": "Delivered"},
                    {"value": "cancelled", "label": "Cancelled"},
                ],
            ),
        ],
        bulk_actions=[
            BulkAction(label="Delete Selected", icon="trash", action_name="delete_selected", style="danger"),
            BulkAction(label="Mark as Shipped", icon="check", action_name="mark_shipped"),
        ],
        mobile_display=["order_number", "customer", "total", "status"],
    )
    
    # Form configuration
    easix_form_config = FormConfig(
        fieldsets=[
            Fieldset(
                title="Order Information",
                icon="document-text",
                fields=["order_number", "customer", "product", "quantity"],
            ),
            Fieldset(
                title="Status & Notes",
                icon="check-circle",
                fields=["status", "notes"],
            ),
        ],
        submit_label="Save Order",
    )
