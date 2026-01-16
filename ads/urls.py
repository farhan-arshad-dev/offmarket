from django.urls import path

from ads.views import AdCreateView, AdDeleteView, AdDetailView, AdListView, AdUpdateView


app_name = 'ads'

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('create/', AdCreateView.as_view(), name='ad_create'),
    path('<int:pk>/edit/', AdUpdateView.as_view(), name='ad_update'),
    path('<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),
]
