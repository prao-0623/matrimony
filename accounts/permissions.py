from rest_framework.permissions import BasePermission

from .models import StaffStatus


def _active_staff_user(user):
    return bool(
        user
        and user.is_authenticated
        and user.is_active
        and user.status == StaffStatus.ACTIVE
    )


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return _active_staff_user(request.user) and getattr(request.user, 'is_super_admin', False)


class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return _active_staff_user(request.user) and (
            getattr(request.user, 'is_admin', False)
            or getattr(request.user, 'is_super_admin', False)
        )
