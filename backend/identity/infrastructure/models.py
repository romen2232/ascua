"""ORM records for the identity context. Domain logic lives in identity.domain."""

import uuid
from typing import Any, ClassVar

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserRecordManager(BaseUserManager["UserRecord"]):
    def create_user(self, email: str, password: str | None = None, **extra: Any) -> "UserRecord":
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user


class UserRecord(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    objects: ClassVar[UserRecordManager] = UserRecordManager()

    class Meta:
        db_table = "identity_user"
