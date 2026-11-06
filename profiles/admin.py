from django.contrib import admin
from django import forms

from .models import Profile


class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ('profile_code', 'full_name', 'profession', 'status', 'gender', 'created_at')
    list_filter = ('status', 'gender', 'marital_status', 'income_range', 'consent_status')
    search_fields = ('profile_code', 'full_name', 'profession', 'mother_tongue')
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'archived_at', 'archived_by')
    ordering = ('-created_at',)

    def _can_manage_profiles(self, request):
        user = request.user
        return bool(
            user.is_superuser
            or getattr(user, 'is_admin', False)
            or getattr(user, 'is_super_admin', False)
        )

    def has_module_permission(self, request):
        return self._can_manage_profiles(request)

    def has_view_permission(self, request, obj=None):
        return self._can_manage_profiles(request)

    def has_add_permission(self, request):
        return self._can_manage_profiles(request)

    def has_change_permission(self, request, obj=None):
        return self._can_manage_profiles(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change and obj.created_by_id is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)