from django import forms
from django.forms import inlineformset_factory

from ads.models import Ad, AdImage
from core.forms.mixins import BootstrapWidgetMixin


class AdForm(BootstrapWidgetMixin, forms.ModelForm):

    class Meta:
        model = Ad
        fields = ['category', 'brand', 'title', 'description', 'location',
                  'city', 'neighbourhood', 'price', 'show_phone_number']


AdImageCreateFormSet = inlineformset_factory(
    Ad,
    AdImage,
    fields=('image',),
    extra=3,
    can_delete=False
)


AdImageUpdateFormSet = inlineformset_factory(
    Ad,
    AdImage,
    fields=('image',),
    extra=3,
    can_delete=True
)
