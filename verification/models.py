import uuid

from django.conf import settings
from django.db import models

from profiles.models import Profile


class VerificationType(models.TextChoices):
    PHONE = 'PHONE', 'Phone'
    EMAIL = 'EMAIL', 'Email'
    PHOTO = 'PHOTO', 'Photo'
    IDENTITY = 'IDENTITY', 'Identity'
    MANUAL = 'MANUAL', 'Manual'


class VerificationStatus(models.TextChoices):
    NOT_STARTED = 'NOT_STARTED', 'Not Started'
    PENDING = 'PENDING', 'Pending'
    VERIFIED = 'VERIFIED', 'Verified'
    REJECTED = 'REJECTED', 'Rejected'
    EXPIRED = 'EXPIRED', 'Expired'
    NEEDS_REVIEW = 'NEEDS_REVIEW', 'Needs Review'


class VerificationCheck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='verification_checks')
    verification_type = models.CharField(max_length=25, choices=VerificationType.choices)
    status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.NOT_STARTED)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_checks')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_checks')
    reason_code = models.CharField(max_length=50, blank=True)
    internal_notes = models.TextField(blank=True)
    evidence_storage_key = models.CharField(max_length=255, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'verification_checks'

    def __str__(self):
        return f'{self.profile.profile_code} - {self.verification_type}'
