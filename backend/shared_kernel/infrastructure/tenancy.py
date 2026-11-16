"""Managers for tenant-owned tables. Every query must name the actor it runs for."""

import inspect
from typing import TypeVar

from django.conf import settings
from django.db import models

from shared_kernel.domain.actor import Actor

M = TypeVar("M", bound=models.Model)


class UnscopedQueryError(Exception):
    """Raised when a tenant table is queried without naming an actor."""


class TenantManager(models.Manager[M]):
    def __init__(self, owner_field: str = "owner_id") -> None:
        super().__init__()
        self.owner_field = owner_field

    def get_queryset(self) -> models.QuerySet[M]:
        raise UnscopedQueryError(f"{self.model.__name__} is tenant-scoped: use .for_actor(actor)")

    def for_actor(self, actor: Actor) -> models.QuerySet[M]:
        return super().get_queryset().filter(**{self.owner_field: actor.user_id})

    def all_unscoped_for_system(self, reason: str) -> models.QuerySet[M]:
        """Unscoped access for allow-listed system modules only. RLS still applies."""
        caller = inspect.stack()[1].frame.f_globals.get("__name__", "")
        allowed: list[str] = getattr(settings, "SYSTEM_QUERY_ALLOWLIST", [])
        if caller not in allowed:
            raise PermissionError(f"{caller} may not run unscoped queries ({reason})")
        return super().get_queryset()
