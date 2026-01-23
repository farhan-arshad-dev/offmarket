from django.conf import settings
from django.db import models
from django.forms import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=96)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE,
        db_index=True
    )
    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def has_parent(self):
        return self.parent is not None

    def get_parent(self):
        return self.parent

    def get_hierarchy(self):
        current = self
        hierarchy = []
        while current:
            hierarchy.append({'id': current.id, 'name': current.name})
            current = current.get_parent()

        # Reverse to get root -> leaf order
        hierarchy.reverse()
        return hierarchy

    def clean(self):
        # Prevent self-parenting
        if self.parent and self.pk and self.parent_id == self.pk:
            raise ValidationError('Category cannot be parent of itself.')

        # Prevent circular hierarchy
        parent = self.parent
        while parent:
            if parent == self:
                raise ValidationError('Circular category hierarchy is not allowed.')
            parent = parent.parent

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=48)

    def __str__(self):
        return self.name


class City(models.Model):
    location = models.ForeignKey(
        Location,
        related_name='cities',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=48)

    class Meta:
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.name


class Neighbourhood(models.Model):
    city = models.ForeignKey(
        City,
        related_name='neighbourhoods',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=48)

    def get_location_hierarchy(self):
        return {
            'location': {
                'id': self.city.location_id,
                'name': self.city.location.name,
            },
            'city': {
                'id': self.city_id,
                'name': self.city.name,
            },
            'neighbourhood': {
                'id': self.id,
                'name': self.name,
            }
        }

    def __str__(self):
        return self.name


class Ad(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ads'
    )

    # Linked to the deepest (leaf) category only
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='ads'
    )

    title = models.CharField(max_length=80)
    description = models.TextField(max_length=4096)

    # Linked to the deepest (leaf) neighbourhood only
    neighbourhood = models.ForeignKey(Neighbourhood, on_delete=models.PROTECT)

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


class Property(models.Model):
    TEXT = 'text'
    NUMBER = 'number'
    BOOLEAN = 'bool'
    CHOICE = 'choice'

    TYPE_CHOICES = (
        (TEXT, 'Text'),
        (NUMBER, 'Number'),
        (BOOLEAN, 'Boolean'),
        (CHOICE, 'Choice'),
    )

    name = models.CharField(max_length=64)
    data_type = models.CharField(max_length=16, choices=TYPE_CHOICES)

    class Meta:
        verbose_name_plural = 'Properties'

    def __str__(self):
        return self.name


class CategoryProperty(models.Model):
    category = models.ForeignKey(
        Category,
        related_name='category_properties',
        on_delete=models.CASCADE
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    required = models.BooleanField(default=False)

    class Meta:
        unique_together = ('category', 'property')
        verbose_name_plural = 'Category Properties'

    def __str__(self):
        return f'{self.category} - {self.property}'


class CategoryPropertyValue(models.Model):
    category_property = models.ForeignKey(
        CategoryProperty,
        related_name='values',
        on_delete=models.CASCADE
    )
    value = models.CharField(max_length=128)

    depends_on = models.ForeignKey(
        CategoryProperty,
        null=True,
        blank=True,
        related_name='dependent_values',
        on_delete=models.CASCADE
    )

    depends_on_value = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('category_property', 'value')
        verbose_name_plural = 'Category Property Values'

    def __str__(self):
        return f'{self.category_property} -> {self.value}'


class AdPropertyValue(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='property_values')
    prop = models.ForeignKey(Property, on_delete=models.CASCADE)
    value = models.TextField(db_index=True)

    def __str__(self):
        return f'{self.ad.title} -> {self.prop.name}: {self.value}'

    @property
    def typed_value(self):
        """Return the value in its proper type"""
        dtype = self.prop.data_type
        if dtype == Property.NUMBER:
            try:
                return int(self.value)
            except ValueError:
                return float(self.value)
        elif dtype == Property.BOOLEAN:
            return self.value.lower() in ('true', '1', 'yes')
        else:
            # text/choice
            return self.value
