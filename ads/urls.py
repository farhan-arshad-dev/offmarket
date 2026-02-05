from django.urls import path
from rest_framework.routers import DefaultRouter

from ads.views import AdCreateView, AdDeleteView, AdDetailView, AdListView, AdUpdateView, AdViewSet
from ads.views_ajax import (
    CitiesView, LoadCategoryChildrenView, LoadCategoryPropertiesView, LocationView, NeighbourhoodView,
)


app_name = 'ads'

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('create/', AdCreateView.as_view(), name='ad_create'),
    path('<int:pk>/edit/', AdUpdateView.as_view(), name='ad_update'),
    path('<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),

    path('ajax/category_children/<int:parent_id>/', LoadCategoryChildrenView.as_view(), name='ajax-category-children'),

    path('ajax/locations/', LocationView.as_view(), name='ajax-locations'),
    path('ajax/cities/<int:location_id>/', CitiesView.as_view(), name='ajax-cities'),
    path('ajax/neighbourhoods/<int:city_id>/', NeighbourhoodView.as_view(), name='ajax-neighbourhoods'),

    path('ajax/load-category-properties/', LoadCategoryPropertiesView.as_view(), name='load_category_properties')
]

router = DefaultRouter()
router.register('ads', AdViewSet, basename='ad')

urlpatterns += router.urls
