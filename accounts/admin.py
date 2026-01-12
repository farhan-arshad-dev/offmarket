from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .models import User


class UserAdmin(AuthUserAdmin):
    model = User
    list_display = ('email', 'is_staff')
    ordering = ('email',)
    search_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ("Important Dates", {'fields': ('last_login',)}),
        ('Permissions', {'fields': ('is_staff',
         'is_active', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


admin.site.register(User, UserAdmin)
