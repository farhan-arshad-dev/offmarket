from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ads.models import Category, City, Location, Neighbourhood


@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Location)
@receiver([post_save, post_delete], sender=City)
@receiver([post_save, post_delete], sender=Neighbourhood)
def invalidate_product_cache(sender, instance, **kwargs):
    """
    Invalidate product list caches when a product is created, updated, or deleted
    """
    print('Clearing product cache')

    # Clear product list caches
    cache.delete_pattern('*ad_creation_form*')
