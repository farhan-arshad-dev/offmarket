from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from accounts.choices import Gender
from accounts.models import Profile
from core.serializers import DisplayChoiceField


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(source='profile.profile_pic', required=False, allow_null=True)
    date_of_birth = serializers.DateField(source='profile.date_of_birth', required=False, allow_null=True)
    gender = DisplayChoiceField(choices=Gender.choices, source='profile.gender', required=False, allow_null=True)
    bio = serializers.CharField(source='profile.bio', required=False, allow_blank=True)
    phone_number = serializers.CharField(source='profile.phone_number', required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'profile_pic', 'date_of_birth', 'gender', 'bio', 'phone_number',)
        read_only_fields = ('email',)

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        profile = getattr(instance, 'profile', None)
        if not profile:
            profile = Profile.objects.create(user=instance)

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
