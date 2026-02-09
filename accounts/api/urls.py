from django.urls import path

from accounts.views import UserProfileAPIView


app_name = 'accounts_api'

urlpatterns = [
    path('profile/', UserProfileAPIView.as_view(), name='profile'),
]
