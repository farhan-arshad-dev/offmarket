from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from ads.forms import AdForm, AdImageCreateFormSet, AdImageUpdateFormSet, ProfileInlineForm
from ads.models import Ad


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
        if self.request.POST:
            context['image_formset'] = AdImageCreateFormSet(self.request.POST, self.request.FILES)
            context['profile_form'] = ProfileInlineForm(self.request.POST, instance=self.request.user.profile)
        else:
            context['image_formset'] = AdImageCreateFormSet()
            context['profile_form'] = ProfileInlineForm(instance=self.request.user.profile)
        return context

    @transaction.atomic()
    def form_valid(self, form):
        context = self.get_context_data()

        image_formset = context['image_formset']
        profile_form = context['profile_form']

        if not form.is_valid() or not profile_form.is_valid():
            return super().form_invalid(form)

        try:
            profile_form.save()
            ad = form.save(commit=False)
            ad.user = self.request.user
            ad.save()
            image_formset.instance = ad

            if not image_formset.is_valid():
                return super().form_invalid(form)

            image_formset.save()

            return redirect(self.success_url)
        except Exception:
            return super().form_invalid(form)


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
            context['profile_form'] = ProfileInlineForm(self.request.POST, instance=self.request.user.profile)
        else:
            context['image_formset'] = AdImageUpdateFormSet(instance=ad)
            context['profile_form'] = ProfileInlineForm(instance=self.request.user.profile)

        return context

    @transaction.atomic()
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        profile_form = context['profile_form']

        if not form.is_valid() or not profile_form.is_valid() or not image_formset.is_valid():
            return self.form_invalid(form)

        try:
            profile_form.save()
            ad = form.save(commit=False)
            ad.user = self.request.user
            ad.save()

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
