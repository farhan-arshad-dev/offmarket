from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as AuthLoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.forms import LoginForm, ProfileForm, RegistrationForm, UserUpdateForm
from accounts.models import Profile
from accounts.serializers import UserProfileSerializer


User = get_user_model()


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


class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_profile_link'] = False

        if self.request.POST:
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        user_form = UserUpdateForm(self.request.POST, instance=self.request.user)

        if user_form.is_valid():
            user_form.save()
        return response


class UserProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_object(self):
        return User.objects.select_related('profile').get(id=self.request.user.id)
