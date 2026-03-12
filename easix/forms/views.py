"""
Form Views
Handle create, update, delete, and detail views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.utils import get_fields_from_path
from django.db import transaction
from django.utils import timezone
from typing import Any, Dict, List, Optional

from ..views import get_easix_settings
from .config import FormConfig, Fieldset, FormField


def get_form_config(model: Any) -> FormConfig:
    """Get or create form config for model."""
    # Check for custom config in model
    if hasattr(model, "easix_form_config"):
        return model.easix_form_config
    
    # Auto-generate config
    return FormConfig.from_model(model)


def normalize_config(config: FormConfig) -> FormConfig:
    """Return a copy of config with all string field refs converted to FormField objects."""
    from dataclasses import replace
    from .config import Fieldset as FieldsetCls

    new_fieldsets = []
    for fs in config.fieldsets:
        new_fields = []
        for f in fs.fields:
            if isinstance(f, str):
                new_fields.append(FormField(name=f))
            else:
                new_fields.append(f)
        new_fieldsets.append(FieldsetCls(
            title=fs.title,
            description=fs.description,
            fields=new_fields,
            icon=fs.icon,
            collapsed=fs.collapsed,
            classes=fs.classes,
        ))
    return replace(config, fieldsets=new_fieldsets)


def get_form_fields(config: FormConfig, instance: Optional[Any] = None) -> List[Dict]:
    """Get form fields with metadata."""
    fields = []
    
    for fieldset in config.fieldsets:
        for field_def in fieldset.fields:
            if isinstance(field_def, str):
                field_name = field_def
                model_field = None
                try:
                    model_field = config.model._meta.get_field(field_name)
                except:
                    pass
                
                field_obj = FormField(
                    name=field_name,
                    label=fieldset.get_label(model_field) if hasattr(fieldset, 'get_label') else None,
                )
            else:
                field_obj = field_def
            
            # Skip excluded fields
            if field_obj.name in config.exclude:
                continue
            
            # Get model field
            model_field = None
            try:
                model_field = config.model._meta.get_field(field_obj.name)
            except:
                pass
            
            # Build field data
            field_data = {
                "name": field_obj.name,
                "label": field_obj.get_label(model_field),
                "help_text": field_obj.get_help_text(model_field),
                "required": field_obj.is_required(model_field),
                "type": get_field_type(model_field, field_obj),
                "widget": field_obj.widget or get_default_widget(model_field),
                "placeholder": field_obj.placeholder,
                "initial": get_field_initial(field_obj, instance, model_field),
                "choices": field_obj.choices or get_field_choices(model_field),
                "min_value": field_obj.min_value,
                "max_value": field_obj.max_value,
                "min_length": field_obj.min_length,
                "max_length": field_obj.max_length or (getattr(model_field, 'max_length', None) if model_field else None),
                "step": field_obj.step,
                "prefix": field_obj.prefix,
                "suffix": field_obj.suffix,
                "icon": field_obj.icon,
                "hidden": field_obj.hidden,
                "readonly": field_obj.readonly or field_obj.name in config.readonly_fields,
                "disabled": field_obj.disabled,
                "colspan": field_obj.colspan,
                "show_when": field_obj.show_when,
                "value": get_field_value(instance, field_obj.name) if instance else None,
            }
            
            fields.append(field_data)
    
    return fields


def get_field_type(model_field: Optional[Any], field_obj: FormField) -> str:
    """Get field type for template."""
    from django.db import models
    
    if field_obj.type:
        return field_obj.type
    
    if not model_field:
        return "text"
    
    if isinstance(model_field, (models.BooleanField,)):
        return "boolean"
    elif isinstance(model_field, (models.IntegerField, models.DecimalField, models.FloatField)):
        return "number"
    elif isinstance(model_field, (models.DateField,)):
        return "date"
    elif isinstance(model_field, (models.DateTimeField,)):
        return "datetime"
    elif isinstance(model_field, (models.EmailField,)):
        return "email"
    elif isinstance(model_field, (models.URLField,)):
        return "url"
    elif isinstance(model_field, (models.ImageField, models.FileField)):
        return "file"
    elif isinstance(model_field, (models.TextField,)):
        return "textarea"
    elif hasattr(model_field, "choices") and model_field.choices:
        return "select"
    
    return "text"


def get_default_widget(model_field: Optional[Any]) -> str:
    """Get default widget for field type."""
    from django.db import models
    
    if not model_field:
        return "text"
    
    if isinstance(model_field, (models.TextField,)):
        return "textarea"
    elif isinstance(model_field, (models.BooleanField,)):
        return "checkbox"
    elif isinstance(model_field, (models.DateField,)):
        return "date"
    elif isinstance(model_field, (models.DateTimeField,)):
        return "datetime"
    elif isinstance(model_field, (models.ImageField,)):
        return "image"
    elif isinstance(model_field, (models.FileField,)):
        return "file"
    elif hasattr(model_field, "choices") and model_field.choices:
        return "select"
    
    return "text"


def get_field_choices(model_field: Optional[Any]) -> Optional[List[Dict]]:
    """Get choices for field."""
    if not model_field or not hasattr(model_field, "choices"):
        return None
    
    choices = model_field.choices
    if not choices:
        return None
    
    return [{"value": str(value), "label": str(label)} for value, label in choices]


def get_field_value(instance: Any, field_name: str) -> Any:
    """Get field value from instance."""
    if not instance:
        return None
    
    value = getattr(instance, field_name, None)
    
    # Handle file fields
    if value and hasattr(value, "url"):
        return value.url
    
    return value


def get_field_initial(field_obj: FormField, instance: Optional[Any], model_field: Optional[Any]) -> Any:
    """Get initial value for field."""
    if field_obj.initial is not None:
        if callable(field_obj.initial):
            return field_obj.initial()
        return field_obj.initial
    
    if instance:
        return get_field_value(instance, field_obj.name)
    
    return None


def model_create(request, app_label: str, model_name: str):
    """Create new model instance."""
    from django.apps import apps
    
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, "Model not found.")
        return redirect("easix:dashboard")
    
    config = get_form_config(model)
    easix_settings = get_easix_settings()
    
    if request.method == "POST":
        form_data = request.POST.dict()
        files_data = request.FILES.dict()
        
        # Remove hidden fields
        for field in config.exclude:
            form_data.pop(field, None)
        
        instance = model()
        
        # Set field values
        for field_name, value in form_data.items():
            if hasattr(instance, field_name) and field_name not in config.exclude:
                model_field = None
                try:
                    model_field = model._meta.get_field(field_name)
                except:
                    pass
                
                # Handle boolean fields
                if model_field and isinstance(model_field, models.BooleanField):
                    value = value == "on" if value else False
                
                # Handle file fields
                if field_name in files_data:
                    value = files_data[field_name]
                
                setattr(instance, field_name, value)
        
        try:
            # Call before_save callback
            if config.before_save:
                config.before_save(instance, request)
            
            instance.full_clean()
            instance.save()
            
            # Call after_save callback
            if config.after_save:
                config.after_save(instance, request)
            
            # Log activity
            log_activity(request, model, instance, "created")
            
            success_msg = config.success_message.format(model=model._meta.verbose_name.title())
            messages.success(request, success_msg)
            
            if request.htmx:
                return redirect("easix:model_detail", app_label=app_label, model_name=model_name, pk=instance.pk)
            
            return redirect("easix:model_list", app_label=app_label, model_name=model_name)
        
        except Exception as e:
            messages.error(request, f"{config.error_message} {str(e)}")
    
    norm_config = normalize_config(config)
    context = {
        "model": model,
        "config": norm_config,
        "fields": {f["name"]: f for f in get_form_fields(config)},
        "easix_settings": easix_settings,
        "page_title": f"Create New {model._meta.verbose_name.title()}",
        "action": "create",
        "submit_label": config.submit_label,
    }
    
    return render(request, "easix/pages/model_form.html", context)


def model_update(request, app_label: str, model_name: str, pk: int):
    """Update existing model instance."""
    from django.apps import apps
    
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, "Model not found.")
        return redirect("easix:dashboard")
    
    instance = get_object_or_404(model, pk=pk)
    config = get_form_config(model)
    easix_settings = get_easix_settings()
    
    if request.method == "POST":
        form_data = request.POST.dict()
        files_data = request.FILES.dict()
        
        # Remove hidden fields
        for field in config.exclude:
            form_data.pop(field, None)
        
        # Set field values
        for field_name, value in form_data.items():
            if hasattr(instance, field_name) and field_name not in config.exclude:
                model_field = None
                try:
                    model_field = model._meta.get_field(field_name)
                except:
                    pass
                
                # Handle boolean fields
                if model_field and isinstance(model_field, models.BooleanField):
                    value = value == "on" if value else False
                
                # Handle file fields
                if field_name in files_data:
                    value = files_data[field_name]
                
                setattr(instance, field_name, value)
        
        try:
            # Call before_save callback
            if config.before_save:
                config.before_save(instance, request)
            
            instance.full_clean()
            instance.save()
            
            # Call after_save callback
            if config.after_save:
                config.after_save(instance, request)
            
            # Log activity
            log_activity(request, model, instance, "updated")
            
            success_msg = config.success_message.format(model=model._meta.verbose_name.title())
            messages.success(request, success_msg)
            
            if request.htmx:
                return redirect("easix:model_detail", app_label=app_label, model_name=model_name, pk=instance.pk)
            
            return redirect("easix:model_list", app_label=app_label, model_name=model_name)
        
        except Exception as e:
            messages.error(request, f"{config.error_message} {str(e)}")
    
    norm_config = normalize_config(config)
    context = {
        "model": model,
        "config": norm_config,
        "instance": instance,
        "fields": {f["name"]: f for f in get_form_fields(config, instance)},
        "easix_settings": easix_settings,
        "page_title": f"Edit {model._meta.verbose_name.title()}",
        "action": "update",
        "submit_label": config.submit_label,
    }
    
    return render(request, "easix/pages/model_form.html", context)


def model_detail(request, app_label: str, model_name: str, pk: int):
    """View model instance details."""
    from django.apps import apps
    
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, "Model not found.")
        return redirect("easix:dashboard")
    
    instance = get_object_or_404(model, pk=pk)
    config = get_form_config(model)
    easix_settings = get_easix_settings()
    
    context = {
        "model": model,
        "config": config,
        "instance": instance,
        "fields": get_form_fields(config, instance),
        "easix_settings": easix_settings,
        "page_title": str(instance),
    }
    
    return render(request, "easix/pages/model_detail.html", context)


def model_delete(request, app_label: str, model_name: str, pk: int):
    """Delete model instance."""
    from django.apps import apps
    
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, "Model not found.")
        return redirect("easix:dashboard")
    
    instance = get_object_or_404(model, pk=pk)
    
    if request.method == "POST":
        try:
            str_instance = str(instance)
            instance.delete()
            
            # Log activity
            log_activity(request, model, instance, "deleted", extra={"name": str_instance})
            
            messages.success(request, f"{model._meta.verbose_name.title()} deleted successfully.")
            
            if request.htmx:
                return redirect("easix:model_list", app_label=app_label, model_name=model_name)
            
            return redirect("easix:model_list", app_label=app_label, model_name=model_name)
        
        except Exception as e:
            # Friendly error message
            error_msg = str(e)
            if "foreign key" in error_msg.lower() or "constraint" in error_msg.lower():
                messages.error(
                    request,
                    f"This {model._meta.verbose_name} cannot be deleted because it is used elsewhere."
                )
            else:
                messages.error(request, f"Error deleting {model._meta.verbose_name}: {error_msg}")
    
    context = {
        "model": model,
        "instance": instance,
        "easix_settings": get_easix_settings(),
        "page_title": f"Delete {model._meta.verbose_name.title()}",
    }
    
    return render(request, "easix/pages/model_delete.html", context)


def model_duplicate(request, app_label: str, model_name: str, pk: int):
    """Duplicate model instance."""
    from django.apps import apps
    
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, "Model not found.")
        return redirect("easix:dashboard")
    
    original = get_object_or_404(model, pk=pk)
    
    # Get all field values except primary key
    field_values = {}
    for field in model._meta.fields:
        if not field.primary_key:
            value = getattr(original, field.name)
            field_values[field.name] = value
    
    # Create new instance
    new_instance = model(**field_values)
    
    try:
        new_instance.save()
        
        # Log activity
        log_activity(request, model, new_instance, "duplicated", extra={"original": str(original)})
        
        messages.success(request, f"{model._meta.verbose_name.title()} duplicated successfully.")
        
        return redirect("easix:model_update", app_label=app_label, model_name=model_name, pk=new_instance.pk)
    
    except Exception as e:
        messages.error(request, f"Error duplicating: {str(e)}")
        return redirect("easix:model_detail", app_label=app_label, model_name=model_name, pk=pk)


def log_activity(request, model, instance, action: str, extra: Optional[Dict] = None):
    """Log activity for audit trail."""
    try:
        from ..activity.models import ActivityLog
        
        ActivityLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=action,
            model_name=model._meta.label,
            object_id=str(instance.pk),
            object_str=str(instance),
            extra=extra or {},
        )
    except Exception:
        pass  # Don't fail if activity logging fails
