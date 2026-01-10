from django.urls import include, path
from .views import RegistrationView, LoginView, LogoutView

app_name = 'accounts'
urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),

    # Use default views for login and logout for now.
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
