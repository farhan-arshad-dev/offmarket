from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from accounts.models import Profile
from core.forms.mixins import BootstrapWidgetMixin


User = get_user_model()


class RegistrationForm(BootstrapWidgetMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class LoginForm(BootstrapWidgetMixin, AuthenticationForm):
    pass


class ProfileForm(forms.ModelForm):

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False
    )

    class Meta:
        model = Profile
        fields = ['profile_pic', 'full_name', 'date_of_birth',
                  'gender', 'bio', 'phone_number']
