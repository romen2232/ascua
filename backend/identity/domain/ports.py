"""What the identity domain needs from the outside world."""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from identity.domain.email import Email
from identity.domain.invitation import Invitation
from identity.domain.user import User


class UserRepository(Protocol):
    def get_by_email(self, email: Email) -> User | None: ...
    def get(self, user_id: UUID) -> User: ...
    def add(self, user: User, password: str) -> None: ...
    def save(self, user: User) -> None: ...


class InvitationRepository(Protocol):
    def get_by_token_hash(self, token_hash: str) -> Invitation | None: ...
    def add(self, invitation: Invitation) -> None: ...
    def save(self, invitation: Invitation) -> None: ...


class Clock(Protocol):
    def now(self) -> datetime: ...


class TotpPort(Protocol):
    def create_device(self, user_id: UUID) -> str:
        """Create (or replace) the user's TOTP device and return its otpauth:// URI."""
        ...

    def verify(self, user_id: UUID, code: str) -> bool:
        """True if `code` is valid now (±1 step) and has not been used before."""
        ...


class EnrolmentTokens(Protocol):
    def issue(self, user_id: UUID) -> str: ...

    def read(self, token: str) -> UUID:
        """Return the user id, or raise EnrolmentInvalid if forged or older than 15 minutes."""
        ...
