from django import forms
from django.conf import settings
from django.forms import ValidationError, inlineformset_factory

from accounts.models import Profile
from ads.models import Ad, AdImage, AdPropertyValue, Category, CategoryProperty, Neighbourhood, Property
from core.forms.mixins import BootstrapWidgetMixin
from core.validators import validate_phone


class AdForm(BootstrapWidgetMixin, forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.HiddenInput(), required=True)
    neighbourhood = forms.ModelChoiceField(
        queryset=Neighbourhood.objects.all(), widget=forms.HiddenInput(), required=True
    )

    class Meta:
        model = Ad
        fields = ['category', 'title', 'description', 'neighbourhood', 'price', 'show_phone_number']

    def clean_category(self):
        category = self.cleaned_data.get('category')

        if not category:
            raise forms.ValidationError('Please select a category.')

        if category.children.exists():
            raise forms.ValidationError('Please select a leaf category.')

        return category


class AdImageForm(BootstrapWidgetMixin, forms.ModelForm):
    class Meta:
        model = AdImage
        fields = ['image']


# Creates a ready-to-use inline formset class (parent–child relationship)
AdImageCreateFormSet = inlineformset_factory(
    parent_model=Ad,
    model=AdImage,
    form=AdImageForm,
    fields=('image',),
    extra=2,
    can_delete=False,
    min_num=1,
    max_num=getattr(settings, 'ADS_MAX_IMAGES_PER_AD', 20),
    validate_max=True,
    validate_min=True
)

AdImageUpdateFormSet = inlineformset_factory(
    parent_model=Ad,
    model=AdImage,
    fields=('image',),
    extra=2,
    can_delete=True,
    min_num=1,
    max_num=getattr(settings, 'ADS_MAX_IMAGES_PER_AD', 20),
    validate_max=True,
    validate_min=True
)


class ProfileInlineForm(BootstrapWidgetMixin, forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(validators=[validate_phone])

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and not self.is_bound:
            self.initial['first_name'] = self.user.first_name
            self.initial['last_name'] = self.user.last_name

    def clean_first_name(self):
        value = self.cleaned_data.get('first_name', '').strip()

        if not value:
            raise ValidationError('First name cannot be empty.')
        return value

    def clean_last_name(self):
        value = self.cleaned_data.get('last_name', '').strip()

        if not value:
            raise ValidationError('Last name cannot be empty.')
        return value

    def save(self, commit=True):
        profile = super().save(commit=False)

        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            if commit:
                self.user.save()

        if commit:
            profile.save()

        return profile


class DynamicPropertyForm(BootstrapWidgetMixin, forms.Form):

    def __init__(self, *args, category=None, ad=None, **kwargs):
        super().__init__(*args, **kwargs)

        if not category:
            return

        existing_values = {}

        if ad:
            existing_values = {
                apv.prop_id: apv.value
                for apv in AdPropertyValue.objects.filter(ad=ad)
            }
        category_properties = (
            CategoryProperty.objects.filter(category=category).select_related('property').prefetch_related('values')
        )
        self.prop_ids = []

        for cp in category_properties:
            prop = cp.property
            field_name = f'property_{prop.id}'
            self.prop_ids.append(prop.id)

            initial = None if self.is_bound else existing_values.get(prop.id)

            if prop.data_type == Property.TEXT:
                field = forms.CharField(label=prop.name, required=cp.required, initial=initial)
            elif prop.data_type == Property.NUMBER:
                field = forms.IntegerField(
                    label=prop.name, required=cp.required, initial=int(initial) if initial not in (None, '') else None
                )
            elif prop.data_type == Property.BOOLEAN:
                field = forms.BooleanField(label=prop.name, required=False, initial=initial in ('True', 'true', True))
            elif prop.data_type == Property.CHOICE:
                choices = [('', '---------')]
                choices += [(v.value, v.value) for v in cp.values.all()]
                field = forms.ChoiceField(label=prop.name, choices=choices, required=cp.required, initial=initial)

            self.fields[field_name] = field

        self.apply_bootstrap()
