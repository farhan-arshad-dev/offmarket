from django.urls import include, path
from .views import RegistrationView
from django.contrib.auth import views as auth_views

app_name = 'accounts'
urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),

    # Use default views for login and logout for now.
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
