from django.contrib import admin
from .forms import CustomUserCreationForm
from authentication_app.models import CustomUser
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    fieldsets = (
        (
            'Individual Data',
            {
                'fields': (
                    'custom',
                )
            }
        ),
        *UserAdmin.fieldsets,
    )
