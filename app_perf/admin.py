from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomAdminChangeForm, CustomAdminCreationForm
from .models import Admins


class CustomUserAdmin(UserAdmin):
    add_form = CustomAdminCreationForm
    form = CustomAdminChangeForm
    model = Admins

    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(Admins, CustomUserAdmin)
