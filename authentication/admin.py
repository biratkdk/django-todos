from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'is_email_verified', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_email_verified', 'is_staff', 'is_active')
    list_per_page = 25
    ordering = ('username',)
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Verification', {'fields': ('is_email_verified',)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (
            'Contact',
            {
                'fields': ('email',),
            },
        ),
    )
