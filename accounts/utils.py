def user_profile_pic_path(instance, filename):
    return f'profiles/user_{instance.user.id}/{filename}'
