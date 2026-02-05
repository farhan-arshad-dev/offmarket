from django.contrib.auth import get_user_model
from rest_framework import serializers

from ads.models import Ad, AdImage, AdPropertyValue


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
