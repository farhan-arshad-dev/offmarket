from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from ads.forms import AdForm, AdImageCreateFormSet, AdImageUpdateFormSet, DynamicPropertyForm, ProfileInlineForm
from ads.models import Ad, AdPropertyValue, Category, Property


class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:ad_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = None
        if self.request.POST:
            category_id = self.request.POST.get('category')
            if category_id:
                category = Category.objects.filter(id=category_id).first()
            context['image_formset'] = AdImageCreateFormSet(self.request.POST, self.request.FILES)
            context['profile_form'] = ProfileInlineForm(
                self.request.POST, instance=self.request.user.profile, user=self.request.user
            )
        else:
            category = self.object.category if self.object else None
            context['image_formset'] = AdImageCreateFormSet()
            context['profile_form'] = ProfileInlineForm(instance=self.request.user.profile, user=self.request.user)

        context['property_form'] = DynamicPropertyForm(self.request.POST or None, category=category)
        return context

    @transaction.atomic()
    def form_valid(self, form):
        context = self.get_context_data()

        image_formset = context['image_formset']
        profile_form = context['profile_form']
        property_form = context['property_form']

        if not form.is_valid() or not profile_form.is_valid():
            return super().form_invalid(form)

        profile_form.save()
        ad = form.save(commit=False)
        ad.user = self.request.user
        ad.save()
        image_formset.instance = ad

        if not image_formset.is_valid() or not property_form.is_valid():
            return super().form_invalid(form)

        ad_category_properties = property_form.cleaned_data.items()
        prop_ids = [
            int(field.split('_', 1)[1])
            for field, value in ad_category_properties
            if value not in (None, '', [])
        ]
        properties = Property.objects.in_bulk(prop_ids)

        ad_property_values = [
            AdPropertyValue(
                ad=ad,
                prop=properties[int(field.split('_', 1)[1])],
                value=str(value)
            )
            for field, value in ad_category_properties
            if value not in (None, '', []) and int(field.split('_', 1)[1]) in properties
        ]
        AdPropertyValue.objects.bulk_create(ad_property_values)
        image_formset.save()
        return redirect(self.success_url)


class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:ad_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.object

        if self.request.POST:
            context['image_formset'] = AdImageUpdateFormSet(self.request.POST, self.request.FILES, instance=ad)
            context['profile_form'] = ProfileInlineForm(
                self.request.POST, instance=self.request.user.profile, user=self.request.user
            )
        else:
            context['image_formset'] = AdImageUpdateFormSet(instance=ad)
            context['profile_form'] = ProfileInlineForm(instance=self.request.user.profile, user=self.request.user)

        print(self.request.method)
        print(ad)
        print(ad.category)
        context['property_form'] = DynamicPropertyForm(self.request.POST or None, category=ad.category, ad=ad)
        context['page_context'] = {
            'category_hierarchy' : ad.category.get_hierarchy(),
            'location_hierarchy' : ad.neighbourhood.get_location_hierarchy(),
        }

        return context

    @transaction.atomic()
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        profile_form = context['profile_form']
        property_form = context['property_form']

        if (not form.is_valid() or not profile_form.is_valid() or not image_formset.is_valid()
                or not property_form.is_valid()):
            return self.form_invalid(form)

        try:
            profile_form.save()
            ad = form.save(commit=False)
            ad.user = self.request.user
            ad.save()

            AdPropertyValue.objects.filter(ad=ad).delete()

            ad_property_values = []
            properties = Property.objects.in_bulk(property_form.prop_ids)

            for field, value in property_form.cleaned_data.items():
                if value in (None, '', []):
                    continue

                prop_id = int(field.split('_', 1)[1])
                if prop_id not in properties:
                    continue

                ad_property_values.append(
                    AdPropertyValue(
                        ad=ad,
                        prop=properties[prop_id],
                        value=str(value)
                    )
                )

            AdPropertyValue.objects.bulk_create(ad_property_values)

            image_formset.instance = ad
            image_formset.save()

            return redirect(self.success_url)
        except Exception:
            return self.form_invalid(form)


class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ads:ad_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
