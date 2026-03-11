"""
Table Configuration Classes
Define table columns, actions, filters, and bulk actions.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Union
from django.db import models
from django.utils.safestring import SafeString


@dataclass
class Column:
    """Define a table column."""
    
    field: str  # Model field name or callable
    label: str  # Display label
    sortable: bool = True
    searchable: bool = False
    visible: bool = True
    width: Optional[str] = None  # CSS width like "150px"
    align: str = "left"  # left, center, right
    format: Optional[Callable] = None  # Format function
    badge: Optional[Dict] = None  # Badge config {True: "success", False: "danger"}
    icon: Optional[str] = None
    type: str = "text"  # text, number, date, datetime, boolean, image, actions
    
    def get_value(self, obj: Any) -> Any:
        """Get value from object for this column."""
        if callable(self.field):
            return self.field(obj)
        
        value = obj
        for part in self.field.split("__"):
            value = getattr(value, part, None)
            if value is None:
                break
        
        if self.format and value is not None:
            return self.format(value)
        
        return value


@dataclass
class Action:
    """Define a row action."""
    
    label: str
    icon: str
    url_pattern: str  # URL pattern or name
    condition: Optional[Callable] = None  # Show condition
    style: str = "default"  # default, primary, danger, success, warning
    target: str = "_self"  # _self, _blank, _modal
    confirm: Optional[str] = None  # Confirmation message


@dataclass
class BulkAction:
    """Define a bulk action."""
    
    label: str
    icon: str
    action_name: str  # Function name to call
    style: str = "default"
    confirm: Optional[str] = None
    condition: Optional[Callable] = None  # Show condition


@dataclass
class Filter:
    """Define a table filter."""
    
    field: str
    label: str
    type: str = "select"  # select, multiselect, text, date, date_range, boolean
    options: Optional[List[Dict]] = None  # For select: [{value, label}]
    queryset: Optional[Any] = None  # For dynamic options
    default: Any = None


@dataclass
class TableConfig:
    """Configure a table."""

    model: Optional[Any] = None  # Django model class (optional, set automatically)
    columns: List[Column] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    bulk_actions: List[BulkAction] = field(default_factory=list)
    filters: List[Filter] = field(default_factory=list)
    per_page: int = 25
    default_sort: str = "-pk"  # Default sorting
    search_fields: List[str] = field(default_factory=list)
    selectable: bool = True
    show_row_actions: bool = True
    mobile_display: List[str] = field(default_factory=list)  # Fields to show on mobile
    template: str = "easix/tables/table.html"
    
    # Callbacks
    get_queryset: Optional[Callable] = None
    preprocess_object: Optional[Callable] = None
    
    @classmethod
    def from_model(cls, model: Any, **kwargs) -> "TableConfig":
        """Create table config from model with sensible defaults."""
        
        # Auto-generate columns from model fields
        columns = []
        for field in model._meta.fields:
            if isinstance(field, (models.AutoField,)):
                continue
            
            label = field.verbose_name.title() if hasattr(field, "verbose_name") else field.name.title()
            
            col_type = "text"
            if isinstance(field, (models.IntegerField, models.DecimalField, models.FloatField)):
                col_type = "number"
            elif isinstance(field, (models.DateField,)):
                col_type = "date"
            elif isinstance(field, (models.DateTimeField,)):
                col_type = "datetime"
            elif isinstance(field, (models.BooleanField,)):
                col_type = "boolean"
            elif isinstance(field, (models.ImageField, models.FileField)):
                col_type = "image"
            
            columns.append(Column(
                field=field.name,
                label=label,
                type=col_type,
                sortable=True,
            ))
        
        # Default actions
        actions = [
            Action(label="View", icon="eye", url_pattern="easix:model_detail", style="default"),
            Action(label="Edit", icon="pencil", url_pattern="easix:model_update", style="primary"),
            Action(label="Delete", icon="trash", url_pattern="easix:model_delete", style="danger",
                   confirm="Are you sure you want to delete this item?"),
        ]
        
        # Default bulk actions
        bulk_actions = [
            BulkAction(label="Delete Selected", icon="trash", action_name="delete_selected",
                       style="danger", confirm="Are you sure you want to delete the selected items?"),
        ]
        
        # Default search fields
        search_fields = []
        for field in model._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                search_fields.append(field.name)
        
        config = cls(
            model=model,
            columns=columns,
            actions=actions,
            bulk_actions=bulk_actions,
            search_fields=search_fields[:5],  # Limit to 5 fields
            **kwargs
        )
        
        # Set mobile display fields (first 2-3 columns)
        if not config.mobile_display:
            config.mobile_display = [col.field for col in columns[:3]]
        
        return config


# Pre-built column types
class FormattedColumn(Column):
    """Column with custom formatting."""
    
    def __init__(self, field: str, label: str, format_func: Callable, **kwargs):
        super().__init__(field=field, label=label, format=format_func, **kwargs)


class BadgeColumn(Column):
    """Column that displays values as badges."""
    
    def __init__(self, field: str, label: str, badge_map: Dict, **kwargs):
        super().__init__(field=field, label=label, badge=badge_map, **kwargs)


class ActionColumn(Column):
    """Column for inline actions."""
    
    def __init__(self, label: str = "Actions", actions: Optional[List[Action]] = None, **kwargs):
        super().__init__(field="", label=label, type="actions", **kwargs)
        self.inline_actions = actions or []
