from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView as AuthLogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import LoginForm, RegistrationForm


class RegistrationView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('dashboard:dashboard')

    def form_valid(self, form):
        is_valid = super().form_valid(form)
        user = self.object
        # auto-login after signup
        login(self.request, user)
        return is_valid


class LoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm


class LogoutView(AuthLogoutView):
    pass
