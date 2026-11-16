"""In-memory implementations of identity ports for application-layer tests."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from identity.domain.email import Email
from identity.domain.invitation import Invitation
from identity.domain.user import User


class FakeClock:
    def __init__(self, now: datetime = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)) -> None:
        self.current = now

    def now(self) -> datetime:
        return self.current

    def advance(self, delta: timedelta) -> None:
        self.current += delta


class FakeUsers:
    def __init__(self) -> None:
        self.by_id: dict[UUID, User] = {}
        self.passwords: dict[UUID, str] = {}

    def get(self, user_id: UUID) -> User:
        return self.by_id[user_id]

    def get_by_email(self, email: Email) -> User | None:
        return next((u for u in self.by_id.values() if u.email == email), None)

    def add(self, user: User, password: str) -> None:
        self.by_id[user.id] = user
        self.passwords[user.id] = password

    def save(self, user: User) -> None:
        self.by_id[user.id] = user


class FakeInvitations:
    def __init__(self) -> None:
        self.items: dict[str, Invitation] = {}

    def get_by_token_hash(self, token_hash: str) -> Invitation | None:
        return self.items.get(token_hash)

    def add(self, invitation: Invitation) -> None:
        self.items[invitation.token_hash] = invitation

    def save(self, invitation: Invitation) -> None:
        self.items[invitation.token_hash] = invitation


class FakeTotp:
    VALID = "123456"

    def __init__(self) -> None:
        self.devices: set[UUID] = set()

    def create_device(self, user_id: UUID) -> str:
        self.devices.add(user_id)
        return f"otpauth://totp/ascua:{user_id}?secret=ABC"

    def verify(self, user_id: UUID, code: str) -> bool:
        return user_id in self.devices and code == self.VALID


class FakeEnrolmentTokens:
    def issue(self, user_id: UUID) -> str:
        return f"enrol:{user_id}"

    def read(self, token: str) -> UUID:
        from identity.domain.errors import EnrolmentInvalid

        if not token.startswith("enrol:"):
            raise EnrolmentInvalid
        return UUID(token.removeprefix("enrol:"))
