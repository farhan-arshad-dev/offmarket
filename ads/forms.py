from django import forms
from django.conf import settings
from django.forms import BaseInlineFormSet, ValidationError, inlineformset_factory

from accounts.models import Profile
from ads.models import Ad, AdImage
from core.forms.mixins import BootstrapWidgetMixin
from core.validators import validate_phone


class AdForm(BootstrapWidgetMixin, forms.ModelForm):

    class Meta:
        model = Ad
        fields = ['category', 'brand', 'title', 'description', 'location',
                  'city', 'neighbourhood', 'price', 'show_phone_number']

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
