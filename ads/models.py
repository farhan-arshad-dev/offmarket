from django.conf import settings
from django.db import models
from django.forms import ValidationError


class Ad(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ads'
    )

    category = models.CharField(max_length=96)
    brand = models.CharField(max_length=96)
    title = models.CharField(max_length=80)
    description = models.TextField(max_length=4096)
    location = models.CharField(max_length=48)
    city = models.CharField(max_length=48)
    neighbourhood = models.CharField(max_length=48)
    price = models.PositiveBigIntegerField()
    show_phone_number = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class AdImage(models.Model):
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='ads/')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
        Define the Model-level Safety Check to restrict the max number of images
        """
        max_images = getattr(settings, 'ADS_MAX_IMAGES_PER_AD', 20)
        max_size_mb = getattr(settings, 'ADS_MAX_IMAGE_SIZE_MB', 5)

        # Max images per Ad
        if self.ad and self.pk:
            if self.ad.images.count() >= max_images:
                raise ValidationError(
                    f'Maximum {max_images} images are allowed per Ad.'
                )

        # Image size limit
        if self.image:
            size_mb = self.image.size / (1024 * 1024)
            if size_mb > max_size_mb:
                raise ValidationError(
                    f'Image size must be less than {max_size_mb} MB.'
                )

    def save(self, *args, **kwargs):
        """
        Enforce validations everywhere
        Manually trigger the complete validation process
        """
        self.full_clean()
        super().save(*args, **kwargs)
