from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from ads.forms import AdForm, AdImageCreateFormSet, AdImageUpdateFormSet
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
            context['image_formset'] = AdImageCreateFormSet(
                self.request.POST,
                self.request.FILES
            )
        else:
            context['image_formset'] = AdImageCreateFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        form.instance.user = self.request.user

        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return redirect(self.success_url)

        return self.form_invalid(form)


class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:ad_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = AdImageUpdateFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['image_formset'] = AdImageUpdateFormSet(
                instance=self.object
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']

        if image_formset.is_valid():
            self.object = form.save()
            image_formset.save()
            return redirect(self.success_url)

        return self.form_invalid(form)


class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ads:ad_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
