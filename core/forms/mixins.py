class BootstrapWidgetMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # SAFETY GUARD
        if not hasattr(self, 'fields') or self.fields is None:
            return

        for field in self.fields.values():
            widget = field.widget
            widget_class = widget.__class__.__name__

            if widget_class in (
                'TextInput', 'EmailInput', 'NumberInput',
                'URLInput', 'PasswordInput', 'Textarea',
                'Select', 'DateInput'
            ):
                widget.attrs.setdefault('class', '')
                widget.attrs['class'] += ' form-control'

            elif widget_class == 'CheckboxInput':
                widget.attrs.setdefault('class', '')
                widget.attrs['class'] += ' form-check-input'

            elif widget_class == 'ClearableFileInput':
                widget.attrs.setdefault('class', '')
                widget.attrs['class'] += ' form-control'
