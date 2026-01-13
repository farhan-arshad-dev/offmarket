from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView as AuthLogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.forms import LoginForm, ProfileForm, RegistrationForm
from accounts.models import Profile

class RegistrationView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:profile')

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


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('dashboard:dashboard')

    def get_object(self, queryset=None):
        # Return the logged-in user's profile
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_profile_link'] = False
        return context
