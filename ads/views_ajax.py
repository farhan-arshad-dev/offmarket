from django.http import JsonResponse
from django.views import View

from ads.models import Category, City, Location, Neighbourhood


class CategoryChildrenView(View):
    def get(self, request, parent_id):
        children = None
        if (parent_id == 0):
            children = Category.objects.filter(parent_id=None).values('id', 'name')
        else:
            children = Category.objects.filter(parent_id=parent_id).values('id', 'name')

        return JsonResponse({'items': list(children)})


class LocationView(View):
    def get(self, request):
        locations = Location.objects.all().values('id', 'name')
        return JsonResponse({'items': list(locations)})


class CitiesView(View):
    def get(self, request, location_id):
        cities = City.objects.filter(location_id=location_id).values('id', 'name')
        return JsonResponse({'items': list(cities)})


class NeighbourhoodView(View):
    def get(self, request, city_id):
        neighbourhoods = Neighbourhood.objects.filter(city_id=city_id).values('id', 'name')
        return JsonResponse({'items': list(neighbourhoods)})
