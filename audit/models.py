import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_actions')
    action = models.CharField(max_length=120)
    entity_type = models.CharField(max_length=80)
    entity_id = models.CharField(max_length=120, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    request_id = models.CharField(max_length=100, blank=True)
    safe_change_summary = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.action} - {self.entity_type}'
