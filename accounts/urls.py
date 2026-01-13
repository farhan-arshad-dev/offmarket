from django.urls import path
from accounts.views import RegistrationView, LoginView, LogoutView

app_name = 'accounts'
urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),

    # Use default views for login and logout for now.
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
