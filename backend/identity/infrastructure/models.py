"""ORM records for the identity context. Domain logic lives in identity.domain."""

import uuid
from typing import Any, ClassVar

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserRecordManager(BaseUserManager["UserRecord"]):
    def create_user(self, email: str, password: str | None = None, **extra: Any) -> "UserRecord":
        user = self.model(email=email.strip().lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user


class UserRecord(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100, default="")
    locale = models.CharField(max_length=2, choices=[("es", "es"), ("en", "en")], default="es")
    is_admin = models.BooleanField(default=False)
    totp_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    objects: ClassVar[UserRecordManager] = UserRecordManager()

    class Meta:
        db_table = "identity_user"

    def __str__(self) -> str:
        return self.email


class InvitationRecord(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    email = models.EmailField()
    token_hash = models.CharField(max_length=64, unique=True)
    invited_by = models.ForeignKey(UserRecord, on_delete=models.PROTECT, related_name="+")
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "identity_invitation"

    def __str__(self) -> str:
        return self.email
