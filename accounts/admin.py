from django.contrib import admin

from .models import StaffSession, StaffUser


@admin.register(StaffUser)
class StaffUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'status', 'is_active', 'created_at')
    list_filter = ('role', 'status', 'is_active')
    search_fields = ('email', 'phone', 'first_name', 'last_name')


@admin.register(StaffSession)
class StaffSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_jti', 'expires_at', 'revoked_at')
    list_filter = ('revoked_at',)
