"""
Form Configuration Classes
Define form fieldsets, fields, and validation.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Union
from django.db import models
from django import forms
from django.forms import widgets


@dataclass
class FormField:
    """Define a form field."""
    
    name: str  # Model field name
    label: Optional[str] = None  # Display label (auto from model if None)
    type: Optional[str] = None  # Override field type
    widget: Optional[str] = None  # Widget type: text, textarea, select, checkbox, radio, file, image, date, datetime, rich_text
    help_text: Optional[str] = None
    placeholder: Optional[str] = None
    required: Optional[bool] = None
    initial: Any = None
    choices: Optional[List[Dict]] = None  # For select/radio: [{value, label}]
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    step: Optional[Union[int, float]] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    icon: Optional[str] = None
    hidden: bool = False
    readonly: bool = False
    disabled: bool = False
    colspan: int = 1  # Column span for grid layout
    show_when: Optional[Dict] = None  # Conditional display {field: value}
    
    def get_label(self, model_field: Optional[models.Field]) -> str:
        """Get field label."""
        if self.label:
            return self.label
        if model_field and hasattr(model_field, "verbose_name"):
            return model_field.verbose_name.title()
        return self.name.replace("_", " ").title()
    
    def get_help_text(self, model_field: Optional[models.Field]) -> str:
        """Get field help text."""
        if self.help_text:
            return self.help_text
        if model_field and hasattr(model_field, "help_text"):
            return model_field.help_text
        return ""
    
    def is_required(self, model_field: Optional[models.Field]) -> bool:
        """Check if field is required."""
        if self.required is not None:
            return self.required
        if model_field:
            return not model_field.blank
        return True


@dataclass
class Fieldset:
    """Define a fieldset (section) in a form."""
    
    title: str
    description: Optional[str] = None
    fields: List[Union[str, FormField]] = field(default_factory=list)
    icon: Optional[str] = None
    collapsed: bool = False
    classes: str = ""
    
    def get_fields(self, model: Optional[Any] = None) -> List[FormField]:
        """Get FormField objects, converting string field names."""
        result = []
        for f in self.fields:
            if isinstance(f, str):
                model_field = None
                if model:
                    try:
                        model_field = model._meta.get_field(f)
                    except:
                        pass
                result.append(FormField(name=f, label=None, model_field=model_field))
            else:
                result.append(f)
        return result


@dataclass
class FormConfig:
    """Configure a form."""

    model: Optional[Any] = None  # Django model class (optional, set automatically)
    fieldsets: List[Fieldset] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    readonly_fields: List[str] = field(default_factory=list)
    
    # Layout
    layout: str = "vertical"  # vertical, horizontal, grid
    columns: int = 1  # For grid layout
    label_width: str = "w-48"  # For horizontal layout
    
    # Submit
    submit_label: str = "Save"
    submit_icon: str = "check"
    show_cancel: bool = True
    cancel_url: Optional[str] = None
    
    # Messages
    success_message: str = "{model} saved successfully."
    error_message: str = "Please correct the errors below."
    
    # Callbacks
    before_save: Optional[Callable] = None
    after_save: Optional[Callable] = None
    get_initial: Optional[Callable] = None
    
    # Inline forms
    inlines: List[Any] = field(default_factory=list)
    
    @classmethod
    def from_model(cls, model: Any, **kwargs) -> "FormConfig":
        """Create form config from model with sensible defaults."""
        
        # Auto-generate fieldsets from model fields
        fieldsets = []
        current_fields = []
        current_category = "Basic Information"
        
        # Group fields by category
        categories = {
            "Basic Information": [],
            "Content": [],
            "Media": [],
            "Status": [],
            "Dates": [],
            "Advanced": [],
        }
        
        for field in model._meta.fields:
            if isinstance(field, (models.AutoField,)):
                continue
            if field.name in kwargs.get("exclude", []):
                continue
            
            field_name = field.name
            
            # Categorize fields
            if any(x in field_name for x in ["name", "title", "slug", "code", "description"]):
                categories["Basic Information"].append(field_name)
            elif any(x in field_name for x in ["content", "body", "text", "summary"]):
                categories["Content"].append(field_name)
            elif any(x in field_name for x in ["image", "photo", "file", "document", "attachment"]):
                categories["Media"].append(field_name)
            elif any(x in field_name for x in ["status", "active", "published", "enabled", "is_"]):
                categories["Status"].append(field_name)
            elif any(x in field_name for x in ["date", "time", "created", "updated"]):
                categories["Dates"].append(field_name)
            else:
                categories["Advanced"].append(field_name)
        
        # Create fieldsets for non-empty categories
        for category, fields in categories.items():
            if fields:
                fieldsets.append(Fieldset(
                    title=category,
                    fields=fields,
                    icon=cls._get_category_icon(category),
                ))
        
        # Default submit label
        submit_label = kwargs.get("submit_label", f"Save {model._meta.verbose_name.title()}")
        
        return cls(
            model=model,
            fieldsets=fieldsets,
            submit_label=submit_label,
            **kwargs
        )
    
    @staticmethod
    def _get_category_icon(category: str) -> str:
        """Get icon for category."""
        icons = {
            "Basic Information": "information-circle",
            "Content": "document-text",
            "Media": "photograph",
            "Status": "check-circle",
            "Dates": "calendar",
            "Advanced": "cog",
        }
        return icons.get(category, "document")


# Pre-built field types
class ImageField(FormField):
    """Image upload field."""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, widget="image", **kwargs)


class TextField(FormField):
    """Multi-line text field."""
    
    def __init__(self, name: str, rows: int = 4, **kwargs):
        super().__init__(name=name, widget="textarea", **kwargs)
        self.rows = rows


class RichTextField(FormField):
    """Rich text editor field."""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, widget="rich_text", **kwargs)


class SelectField(FormField):
    """Select dropdown field."""
    
    def __init__(self, name: str, choices: List[Dict], **kwargs):
        super().__init__(name=name, widget="select", choices=choices, **kwargs)


class DateField(FormField):
    """Date picker field."""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, widget="date", **kwargs)


class DateTimeField(FormField):
    """Date and time picker field."""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, widget="datetime", **kwargs)
