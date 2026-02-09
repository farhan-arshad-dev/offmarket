from django.urls import path
from rest_framework.routers import DefaultRouter

from ads.views import AdCreateConfigAPIView, AdViewSet


app_name = 'ads_api'

urlpatterns = [
    path('create-ad-form/', AdCreateConfigAPIView.as_view(), name='create_ad_form'),
]

router = DefaultRouter()
router.register('ads', AdViewSet, basename='ad')

urlpatterns += router.urls
