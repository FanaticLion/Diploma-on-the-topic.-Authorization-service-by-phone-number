from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'username', 'email', 'invite_code', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('phone', 'username', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('Реферальная система', {
            'fields': ('phone', 'invite_code', 'activated_invite_code')
        }),
    )