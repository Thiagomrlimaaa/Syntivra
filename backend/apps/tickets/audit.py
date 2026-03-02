from django.db import models
from django.conf import settings
from apps.tenants.models import TenantModel
import uuid

class AuditLog(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_actions'
    )
    action = models.CharField(max_length=255)
    target_model = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100)
    changes = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor} - {self.action} on {self.target_model}"
