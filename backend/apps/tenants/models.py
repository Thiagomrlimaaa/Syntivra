from django.db import models
import uuid
from .utils import get_current_tenant_id

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TenantManager(models.Manager):
    def get_queryset(self):
        tenant_id = get_current_tenant_id()
        queryset = super().get_queryset()
        if tenant_id:
            return queryset.filter(organization_id=tenant_id)
        return queryset

class TenantModel(models.Model):
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name="%(class)s_related",
        null=True,
        blank=True
    )

    objects = TenantManager()
    unfiltered_objects = models.Manager()

    class Meta:
        abstract = True
