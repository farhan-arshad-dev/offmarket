from django.conf import settings
from django.db import models

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
