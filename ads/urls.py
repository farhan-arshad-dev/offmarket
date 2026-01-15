from django.urls import path

from ads.views import AdListView, AdDetailView

app_name = 'ads'

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
]
