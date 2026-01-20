from django.urls import path

from ads.views import AdCreateView, AdDeleteView, AdDetailView, AdListView, AdUpdateView
from ads.views_ajax import CategoryChildrenView, CitiesView, LocationView, NeighbourhoodView


app_name = 'ads'

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('create/', AdCreateView.as_view(), name='ad_create'),
    path('<int:pk>/edit/', AdUpdateView.as_view(), name='ad_update'),
    path('<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),

    path('ajax/categories/<int:parent_id>/', CategoryChildrenView.as_view(), name='ajax-category-children'),

    path('ajax/locations/', LocationView.as_view(), name='ajax-locations'),
    path('ajax/cities/<int:location_id>/', CitiesView.as_view(), name='ajax-cities'),
    path('ajax/neighbourhoods/<int:city_id>/', NeighbourhoodView.as_view(), name='ajax-neighbourhoods'),
]
