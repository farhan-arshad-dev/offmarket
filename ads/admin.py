from django.contrib import admin

from ads.models import Ad, AdImage

admin.site.register((Ad, AdImage,))
