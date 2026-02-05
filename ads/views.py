from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.forms import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ads.forms import AdForm, AdImageCreateFormSet, AdImageUpdateFormSet, DynamicPropertyForm, ProfileInlineForm
from ads.models import Ad, AdPropertyValue, Category, City, Property
from ads.serializers import AdSerializer


class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user', 'category', 'neighbourhood').prefetch_related('images')
        keyword = self.request.GET.get('q', '').strip()
        city_select = self.request.GET.get('city', '')

        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(category__name__icontains=keyword)
            )

        if city_select and city_select.startswith('CITY_'):
            city_id = int(city_select.replace('CITY_', ''))
            queryset = queryset.filter(
                neighbourhood__city_id=city_id
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cities = City.objects.prefetch_related().all()

        city_choices = []
        for city in cities.all():
            city_choices.append((f'CITY_{city.id}', city.name))

        context['city_choices'] = city_choices
        return context


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_queryset(self):
        return super().get_queryset().select_related('user', 'category', 'neighbourhood').prefetch_related('images')

class AdFormMixin(LoginRequiredMixin):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:ad_list')
    image_formset_class = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.object
        post_data = self.request.POST or None
        files_data = self.request.FILES or None

        if post_data:
            context['image_formset'] = self.image_formset_class(post_data, files_data, instance=ad)
            context['profile_form'] = ProfileInlineForm(
                post_data, instance=self.request.user.profile, user=self.request.user
            )
        else:
            context['image_formset'] = self.image_formset_class(instance=ad)
            context['profile_form'] = ProfileInlineForm(instance=self.request.user.profile, user=self.request.user)

        category_id = None

        if ad and ad.category_id:
            category_id = ad.category_id
        else:
            category_id = self.request.POST.get('category')

        category = Category.objects.filter(id=category_id).first()

        context['property_form'] = DynamicPropertyForm(post_data, category=category, ad=ad)

        if ad:
            context['page_context'] = {
                'category_hierarchy': ad.category.get_hierarchy,
                'location_hierarchy': ad.neighbourhood.get_location_hierarchy(),
            }

        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        profile_form = context['profile_form']
        property_form = context['property_form']

        forms_are_valid = all([
            form.is_valid(), profile_form.is_valid(), image_formset.is_valid(), property_form.is_valid(),
        ])

        if not forms_are_valid:
            return self.form_invalid(form)

        try:
            profile_form.save()

            ad = form.save(commit=False)
            ad.user = self.request.user
            ad.save()

            prop_ids = [
                int(field.split('_', 1)[1])
                for field, value in property_form.cleaned_data.items()
                if value not in (None, '', [])
            ]
            properties = Property.objects.in_bulk(prop_ids)

            ad_property_values = [
                AdPropertyValue(ad=ad, prop=properties[int(field.split('_', 1)[1])], value=str(value))
                for field, value in property_form.cleaned_data.items()
                if value not in (None, '', []) and int(field.split('_', 1)[1]) in properties
            ]

            AdPropertyValue.objects.bulk_create(
                ad_property_values, update_conflicts=True, unique_fields=['ad', 'prop'], update_fields=['value']
            )

            image_formset.instance = ad
            image_formset.save()

            return redirect(self.success_url)

        except (ValidationError, IntegrityError) as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

class AdCreateView(AdFormMixin, CreateView):
    image_formset_class = AdImageCreateFormSet


class AdUpdateView(AdFormMixin, UpdateView):
    image_formset_class = AdImageUpdateFormSet

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ads:ad_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class AdViewSet(viewsets.ModelViewSet):
    queryset = (
        Ad.objects.select_related('user', 'user__profile', 'category', 'neighbourhood', 'neighbourhood__city',
                                  'neighbourhood__city__location').prefetch_related('images', 'property_values__prop')
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        return AdSerializer
