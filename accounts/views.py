from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import RegistrationForm


class RegistrationView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('dashboard:dashboard')

    def form_valid(self, form):
        # call super method to process the request e.g validate the use info and save in db.
        is_valid = super().form_valid(form)
        # After success of creating user, now can access the newly created use object via self.object
        user = self.object
        # auto-login after signup
        login(self.request, user)
        return is_valid
