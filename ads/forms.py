from django import forms
from django.conf import settings
from django.forms import BaseInlineFormSet, ValidationError, inlineformset_factory

from accounts.models import Profile
from ads.models import Ad, AdImage, AdPropertyValue, Category, CategoryProperty, Neighbourhood, Property
from core.forms.mixins import BootstrapWidgetMixin
from core.validators import validate_phone


class AdForm(BootstrapWidgetMixin, forms.ModelForm):

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.HiddenInput(),
        required=True
    )

    neighbourhood = forms.ModelChoiceField(
        queryset=Neighbourhood.objects.all(),
        widget=forms.HiddenInput(),
        required=True
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

    def clean_image(self):
        """
        Define Formset Level (Sync with settings) to restrict the max size of images
        """
        image = self.cleaned_data.get('image')
        max_size_mb = getattr(settings, 'ADS_MAX_IMAGE_SIZE_MB', 5)

        if image:
            size_mb = image.size / (1024 * 1024)
            if size_mb > max_size_mb:
                raise forms.ValidationError(
                    f'Image size must be under {max_size_mb} MB.'
                )

        return image


class AdImageBaseFormSet(BootstrapWidgetMixin, BaseInlineFormSet):
    """
    Class used to control the validation and behavior of inline formsets.
    Rules + behavior engine for inline formsets
    """
    def clean(self):
        """
        Define Formset Level (Sync with settings) to restrict the max number of images
        """
        super().clean()

        max_images = getattr(settings, 'ADS_MAX_IMAGES_PER_AD', 20)

        total_images = 0
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            if form.cleaned_data.get('image'):
                total_images += 1

        if total_images > max_images:
            raise forms.ValidationError(
                f'You can upload a maximum of {max_images} images.'
            )
        if total_images < 1:
            raise forms.ValidationError('You need upload a atleast 1 image.')


# Creates a ready-to-use inline formset class (parent–child relationship)
AdImageCreateFormSet = inlineformset_factory(
    parent_model=Ad,
    model=AdImage,
    form=AdImageForm,
    formset=AdImageBaseFormSet,
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
    formset=AdImageBaseFormSet,
    fields=('image',),
    extra=2,
    can_delete=True,
    min_num=1,
    max_num=getattr(settings, 'ADS_MAX_IMAGES_PER_AD', 20),
    validate_max=True,
    validate_min=True
)

class ProfileInlineForm(forms.ModelForm):

    phone_number = forms.CharField(
        validators=[validate_phone],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Profile
        fields = ['full_name', 'phone_number']
        widgets = {'full_name': forms.TextInput(attrs={'class': 'form-control'})}

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if not full_name or not full_name.strip():
            raise ValidationError('Full name cannot be empty.')
        return full_name.strip()


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
        print('*' * 20)
        print(ad)
        print(AdPropertyValue.objects.filter(ad=ad))
        print(existing_values)

        category_properties = (
            CategoryProperty.objects
            .filter(category=category)
            .select_related('property')
            .prefetch_related('values')
        )
        self.prop_ids = []

        for cp in category_properties:
            prop = cp.property
            field_name = f'property_{prop.id}'
            self.prop_ids.append(prop.id)

            initial = None if self.is_bound else existing_values.get(prop.id)

            if prop.data_type == Property.TEXT:
                field = forms.CharField(
                    label=prop.name,
                    required=cp.required,
                    initial=initial
                )

            elif prop.data_type == Property.NUMBER:
                field = forms.IntegerField(
                    label=prop.name,
                    required=cp.required,
                    initial=int(initial) if initial not in (None, '') else None
                )

            elif prop.data_type == Property.BOOLEAN:
                field = forms.BooleanField(
                    label=prop.name,
                    required=False,
                    initial=initial in ('True', 'true', True)
                )

            elif prop.data_type == Property.CHOICE:
                choices = [('', '---------')]
                choices += [(v.value, v.value) for v in cp.values.all()]

                field = forms.ChoiceField(
                    label=prop.name,
                    choices=choices,
                    required=cp.required,
                    initial=initial
                )

            self.fields[field_name] = field

        self.apply_bootstrap()
