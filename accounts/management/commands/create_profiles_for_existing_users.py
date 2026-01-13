from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Profile


User = get_user_model()


class Command(BaseCommand):
    help = 'Create profile objects for existing users who do not have one'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(profile__isnull=True)
        for user in users_without_profile:
            Profile.objects.create(user=user)
        self.stdout.write(self.style.SUCCESS(
            f'Created {len(users_without_profile)} profiles'))
