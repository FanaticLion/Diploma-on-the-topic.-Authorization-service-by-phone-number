from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AuthCode


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'username', 'email', 'invite_code', 'activated_invite_code', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('phone', 'username', 'email', 'invite_code')
    readonly_fields = ('invite_code', 'created_at')

    fieldsets = UserAdmin.fieldsets + (
        ('Реферальная система', {
            'fields': ('phone', 'invite_code', 'activated_invite_code', 'created_at')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2'),
        }),
    )


@admin.register(AuthCode)
class AuthCodeAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code', 'created_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('phone', 'code')
    readonly_fields = ('created_at',)