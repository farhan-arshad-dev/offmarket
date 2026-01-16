from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from accounts.choices import Gender
from accounts.managers import UserManager
from accounts.utils import user_profile_pic_path
from core.models.base import BaseModel


class User(AbstractUser, BaseModel):
    objects = UserManager()

    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def full_name(self):
        return super().get_full_name()

    def __str__(self):
        return self.email


class Profile(BaseModel):
    phone_regex = RegexValidator(regex=r'^\+?[1-9]\d{7,14}$', message='Enter a valid international phone number.')
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.ImageField(upload_to=user_profile_pic_path, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, null=True, blank=True)
    bio = models.TextField(blank=True, max_length=200)

    phone_number = models.CharField(validators=[phone_regex], max_length=16, blank=True, null=True)

    def __str__(self):
        return self.user.full_name
