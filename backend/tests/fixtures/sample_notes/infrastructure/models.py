import uuid

from django.db import models

from shared_kernel.infrastructure.tenancy import TenantManager


class SampleNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_id = models.UUIDField()
    text = models.CharField(max_length=200)

    objects = TenantManager["SampleNote"]()

    def __str__(self) -> str:
        return self.text
