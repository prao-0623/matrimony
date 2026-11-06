import uuid

from django.conf import settings
from django.db import models

from profiles.models import Profile


class PaymentStatus(models.TextChoices):
    INITIATED = 'INITIATED', 'Initiated'
    PENDING = 'PENDING', 'Pending'
    SUCCEEDED = 'SUCCEEDED', 'Succeeded'
    FAILED = 'FAILED', 'Failed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    REFUND_PENDING = 'REFUND_PENDING', 'Refund Pending'
    REFUNDED = 'REFUNDED', 'Refunded'
    PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED', 'Partially Refunded'


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='payments')
    amount_minor = models.BigIntegerField()
    currency = models.CharField(max_length=5, default='INR')
    purpose = models.CharField(max_length=120)
    payment_method = models.CharField(max_length=40, default='MANUAL')
    provider = models.CharField(max_length=80, blank=True)
    provider_reference = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=24, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_payments')
    paid_at = models.DateTimeField(null=True, blank=True)
    reconciliation_status = models.CharField(max_length=20, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_transactions'

    def __str__(self):
        return f'{self.profile.profile_code} - {self.amount_minor}'
