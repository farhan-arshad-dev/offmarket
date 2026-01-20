from django.contrib import admin

from ads.models import (
    Ad, AdImage, AdPropertyValue, Category, CategoryProperty, CategoryPropertyValue, City, Location, Neighbourhood,
    Property,
)


class AdImageInline(admin.StackedInline):
    model = AdImage
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'ad'


class AdPropertyValueAdmin(admin.StackedInline):
    model = AdPropertyValue
    can_delete = True
    verbose_name_plural = 'AdPropertyValues'
    fk_name = 'ad'


@admin.register(Ad)
class AdModelAdmin(admin.ModelAdmin):
    inlines = [AdPropertyValueAdmin, AdImageInline]
    list_display = ('title', 'category', 'price')
    ordering = ('title',)
    search_fields = ('title',)


class CategoryPropertyInline(admin.TabularInline):
    model = CategoryProperty
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('is_active',)
    inlines = [CategoryPropertyInline]


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_type')


class CategoryPropertyValueInline(admin.TabularInline):
    model = CategoryPropertyValue
    extra = 1
    fk_name = 'category_property'


@admin.register(CategoryProperty)
class CategoryPropertyAdmin(admin.ModelAdmin):
    list_display = ('property', 'category', 'required')
    inlines = [CategoryPropertyValueInline]


admin.site.register(Location)
admin.site.register(City)
admin.site.register(Neighbourhood)
