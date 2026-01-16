from django import forms


class BootstrapWidgetMixin:
    """
    Automatically adds Bootstrap 5 classes to Django form widgets.
    """

    bootstrap_widget_classes = {
        forms.TextInput: 'form-control',
        forms.EmailInput: 'form-control',
        forms.URLInput: 'form-control',
        forms.NumberInput: 'form-control',
        forms.PasswordInput: 'form-control',
        forms.Textarea: 'form-control',
        forms.DateInput: 'form-control',
        forms.DateTimeInput: 'form-control',
        forms.TimeInput: 'form-control',
        forms.Select: 'form-select',
        forms.SelectMultiple: 'form-select',
        forms.FileInput: 'form-control',
        forms.ClearableFileInput: 'form-control',
        forms.CheckboxInput: 'form-check-input',
        forms.RadioSelect: 'form-check-input',
        forms.CheckboxSelectMultiple: 'form-check-input',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # SAFETY GUARD
        if not hasattr(self, 'fields') or self.fields is None:
            return

        for field_name, field in self.fields.items():
            widget = field.widget

            if widget.is_hidden:
                continue

            for widget_type, css_class in self.bootstrap_widget_classes.items():
                if isinstance(widget, widget_type):
                    existing_classes = widget.attrs.get('class', '')
                    widget.attrs['class'] = f'{existing_classes} {css_class}'.strip()
                    break

            # Add placeholder if missing (optional)
            if not widget.attrs.get('placeholder'):
                widget.attrs['placeholder'] = field.label
