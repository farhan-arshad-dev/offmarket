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


class UserUpdateForm(BootstrapWidgetMixin, forms.ModelForm):
    email = forms.EmailField(disabled=True, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(BootstrapWidgetMixin, forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = Profile
        fields = ['profile_pic', 'date_of_birth', 'gender', 'bio', 'phone_number']
