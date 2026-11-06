import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import StaffUserManager


class StaffRole(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
    ADMIN = 'ADMIN', 'Admin'


class StaffStatus(models.TextChoices):
    INVITED = 'INVITED', 'Invited'
    ACTIVE = 'ACTIVE', 'Active'
    DISABLED = 'DISABLED', 'Disabled'


class StaffUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=StaffRole.choices, default=StaffRole.ADMIN)
    status = models.CharField(max_length=20, choices=StaffStatus.choices, default=StaffStatus.ACTIVE)
    created_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_staff',
    )
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = StaffUserManager()

    class Meta:
        db_table = 'staff_users'

    def __str__(self):
        return self.email

    @property
    def is_super_admin(self):
        return self.is_active and self.role == StaffRole.SUPER_ADMIN

    @property
    def is_admin(self):
        return self.is_active and self.role == StaffRole.ADMIN


class StaffSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    token_jti = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'staff_sessions'

    def __str__(self):
        return f'{self.user.email} - {self.token_jti}'
