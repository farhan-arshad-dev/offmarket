from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View

from ads.forms import DynamicPropertyForm
from ads.models import Ad, Category, City, Location, Neighbourhood


class LoadCategoryChildrenView(View):
    def get(self, request, parent_id):
        children = None
        if parent_id == 0:
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


class LoadCategoryPropertiesView(LoginRequiredMixin, View):
    login_url = reverse_lazy('accounts:login')
    # important for AJAX otherwise Without this, Django redirects login page
    redirect_field_name = None

    def get(self, request, *args, **kwargs):
        ad_id = request.GET.get('ad_id')
        category_id = request.GET.get('category_id')
        ad_object = Ad.objects.filter(id=ad_id).first() if ad_id else None
        category = Category.objects.filter(id=category_id).first()

        if not category:
            return JsonResponse({'html': ''})

        form = DynamicPropertyForm(category=category, ad=ad_object)

        html = render_to_string(
            'ads/partials/property_form.html',
            {'property_form': form},
            request=request
        )
        return JsonResponse({'html': html})
