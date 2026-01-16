from django import forms
from django.forms import inlineformset_factory

from ads.models import Ad, AdImage

class AdForm(forms.ModelForm):

    class Meta:
        model = Ad
        fields = ['category', 'brand', 'title', 'description', 'location',
                  'city', 'neighbourhood', 'price', 'show_phone_number']


AdImageFormSet = inlineformset_factory(
    Ad,
    AdImage,
    fields=('image',),
    extra=3,
    can_delete=True
)
