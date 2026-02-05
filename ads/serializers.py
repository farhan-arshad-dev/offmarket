from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from ads.models import (
    Ad, AdImage, AdPropertyValue, Category, CategoryProperty, CategoryPropertyValue, City, Location, Neighbourhood,
    Property,
)


User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(method_name='get_full_name')
    profile_pic = serializers.SerializerMethodField(method_name='get_profile_pic')
    phone_number = serializers.SerializerMethodField(method_name='get_phone_number')

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'profile_pic', 'phone_number')

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip()

    def get_profile_pic(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.profile.profile_pic.url) if obj.profile.profile_pic else None

    def get_phone_number(self, obj):
        show_phone_number = self.context.get('show_phone_number', False)
        request = self.context.get('request')

        if not show_phone_number or not request or not request.user.is_authenticated:
            return None

        return obj.profile.phone_number

class AdImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdImage
        fields = ('id', 'image')
        read_only_fields = ('id',)


class AdPropertyValueSerializer(serializers.ModelSerializer):
    prop_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AdPropertyValue
        fields = ('prop_id', 'value')


class AdSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(method_name='get_user')
    images = AdImageSerializer(many=True, read_only=True)
    property_values = serializers.SerializerMethodField(method_name='get_property_values')
    location = serializers.SerializerMethodField(method_name='get_location')

    class Meta:
        model = Ad
        fields = ('id', 'title', 'description', 'price', 'category', 'location', 'images', 'property_values', 'user',
                  'created_at',)
        read_only_fields = ('id',)

    def get_user(self, obj):
        serializer = UserPublicSerializer(
            obj.user,
            context={
                **self.context,
                'show_phone_number': obj.show_phone_number,
            }
        )
        return serializer.data

    def get_property_values(self, obj):
        return [
            {
                'id': pv.prop.id,
                'name': pv.prop.name,
                'value': pv.typed_value,
            }
            for pv in obj.property_values.select_related('prop')
        ]

    def get_location(self, obj):
        return obj.neighbourhood.get_location_hierarchy()


class AdCreateSerializer(serializers.ModelSerializer):
    images = AdImageSerializer(many=True, read_only=True)
    upload_images = serializers.ListField(child=serializers.ImageField(allow_empty_file=False, use_url=False),
                                          write_only=True, required=False)
    delete_images = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    properties = AdPropertyValueSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Ad
        fields = ('id', 'category', 'title', 'description', 'neighbourhood', 'price', 'show_phone_number', 'images',
                  'properties', 'upload_images', 'delete_images',)
        read_only_fields = ('id',)

    def validate(self, attrs):
        ad = self.instance
        delete_ids = attrs.get('delete_images', [])
        new_images = attrs.get('upload_images', [])

        if delete_ids:
            valid_ids = set(ad.images.filter(id__in=delete_ids).values_list('id', flat=True))
            if len(valid_ids) != len(delete_ids):
                raise serializers.ValidationError({'images': 'One or more images do not belong to this ad.'})

        existing_count = 0

        if ad and ad.images:
            existing_count = ad.images.count()

        final_count = existing_count - len(delete_ids) + len(new_images)

        if final_count < 1:
            raise serializers.ValidationError({'images': 'At least one image is required.'})

        max_images = getattr(settings, 'ADS_MAX_IMAGES_PER_AD', 20)
        if final_count > max_images:
            raise serializers.ValidationError({'images': f'You can upload a maximum of {max_images} images.'})

        category = self.instance.category if self.instance and self.instance.category else attrs.get('category')

        if not category:
            raise serializers.ValidationError({'category': 'Category is required.'})

        if category.children.exists():
            raise serializers.ValidationError({'category': 'You can only post under a leaf category.'})

        if category:
            required_props = CategoryProperty.objects.filter(category=category, is_required=True)
            provided_prop_ids = {pv['prop_id'] for pv in attrs.get('properties', [])}

            missing_props = [prop.property.name for prop in required_props if prop.id not in provided_prop_ids]

            if missing_props:
                raise serializers.ValidationError({
                    'properties': f'Missing required property values: {", ".join(missing_props)}'
                })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        images_data = validated_data.pop('upload_images', [])
        property_values_data = validated_data.pop('properties', [])

        ad = Ad.objects.create(**validated_data)

        AdImage.objects.bulk_create([AdImage(ad=ad, image=image_file) for image_file in images_data])

        prop_ids = [pv['prop_id'] for pv in property_values_data]
        properties = Property.objects.in_bulk(prop_ids)
        ad_property_values = [
            AdPropertyValue(ad=ad, prop=properties[pv['prop_id']], value=pv['value'])
            for pv in property_values_data
            if pv['prop_id'] in properties
        ]
        AdPropertyValue.objects.bulk_create(
            ad_property_values, update_conflicts=True, unique_fields=['ad', 'prop'], update_fields=['value']
        )

        return ad

    @transaction.atomic
    def update(self, instance, validated_data):
        upload_images = validated_data.pop('upload_images', [])
        delete_images = validated_data.pop('delete_images', [])
        property_values_data = validated_data.pop('properties', [])

        if delete_images:
            instance.images.filter(id__in=delete_images).delete()

        if upload_images:
            AdImage.objects.bulk_create([AdImage(ad=instance, image=image_file)for image_file in upload_images])

        if property_values_data:
            prop_ids = [pv['prop_id'] for pv in property_values_data]
            properties = Property.objects.in_bulk(prop_ids)

            AdPropertyValue.objects.bulk_create(
                [
                    AdPropertyValue(ad=instance, prop=properties[pv['prop_id']], value=pv['value'])
                    for pv in property_values_data
                    if pv['prop_id'] in properties
                ],
                update_conflicts=True,
                unique_fields=['ad', 'prop'],
                update_fields=['value']
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CategoryPropertyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryPropertyValue
        fields = ('id', 'value')


class CategoryPropertySerializer(serializers.ModelSerializer):
    values = CategoryPropertyValueSerializer(
        source='category_property_values',  # matches your related_name
        many=True
    )

    class Meta:
        model = CategoryProperty
        fields = ('id', 'property', 'is_required', 'values')


class CategorySerializer(serializers.ModelSerializer):
    properties = CategoryPropertySerializer(many=True, read_only=True, source='category_properties')
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'properties', 'children')

    def get_children(self, obj):
        children_qs = obj.children.all()
        if children_qs.exists():
            serializer = CategorySerializer(children_qs, many=True)
            return serializer.data
        return None

class NeighbourhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighbourhood
        fields = ('id', 'name')


class CityWithNeighbourhoodsSerializer(serializers.ModelSerializer):
    neighbourhoods = NeighbourhoodSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ('id', 'name', 'neighbourhoods')

class LocationWithCitiesSerializer(serializers.ModelSerializer):
    cities = CityWithNeighbourhoodsSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = ('id', 'name', 'cities')
