from django.contrib import admin

from ads.models import Ad, AdImage, Category, City, Location, Neighbourhood


class AdImageInline(admin.StackedInline):
    model = AdImage
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'ad'

@admin.register(Ad)
class AdModelAdmin(admin.ModelAdmin):
    inlines = [AdImageInline]
    list_display = ('title', 'category', 'price')
    ordering = ('title',)
    search_fields = ('title',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('is_active',)


admin.site.register(Location)
admin.site.register(City)
admin.site.register(Neighbourhood)
