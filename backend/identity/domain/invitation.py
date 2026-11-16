"""Invitation aggregate. Only the SHA-256 hash of the token is ever stored."""

import hashlib
import hmac
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID

from identity.domain.email import Email
from shared_kernel.domain.errors import DomainError

TTL = timedelta(days=7)


class InvitationInvalid(DomainError):
    code = "invitation_invalid"
    http_status = 404


class InvitationUsed(DomainError):
    code = "invitation_used"
    http_status = 410


class InvitationExpired(DomainError):
    code = "invitation_expired"
    http_status = 410


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


@dataclass
class Invitation:
    id: UUID
    email: Email
    token_hash: str = field(repr=False)
    invited_by: UUID
    expires_at: datetime
    used_at: datetime | None = None

    @classmethod
    def issue(
        cls, email: Email, invited_by: UUID, now: datetime, token_factory: Callable[[], str]
    ) -> tuple["Invitation", str]:
        raw = token_factory()
        invitation = cls(uuid.uuid4(), email, hash_token(raw), invited_by, now + TTL)
        return invitation, raw

    def accept(self, raw_token: str, now: datetime) -> None:
        if not hmac.compare_digest(hash_token(raw_token), self.token_hash):
            raise InvitationInvalid
        if self.used_at is not None:
            raise InvitationUsed
        if now > self.expires_at:
            raise InvitationExpired
        self.used_at = now
