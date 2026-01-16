from django.contrib import admin

from ads.models import Ad, AdImage


class AdImageInline(admin.StackedInline):
    model = AdImage
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'ad'

@admin.register(Ad)
class AdModelAdmin(admin.ModelAdmin):
    inlines = [AdImageInline]
    list_display = ('title', 'category', 'brand', 'price', 'location')
    ordering = ('title',)
    search_fields = ('title',)
