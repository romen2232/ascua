"""Django implementations of the identity ports."""

from datetime import datetime
from uuid import UUID

from django.utils import timezone

from identity.domain.email import Email
from identity.domain.invitation import Invitation
from identity.domain.user import User
from identity.infrastructure.mappers import (
    invitation_fields,
    invitation_to_domain,
    user_fields,
    user_to_domain,
)
from identity.infrastructure.models import InvitationRecord, UserRecord


class DjangoUserRepository:
    def get(self, user_id: UUID) -> User:
        return user_to_domain(UserRecord.objects.get(pk=user_id))

    def get_by_email(self, email: Email) -> User | None:
        record = UserRecord.objects.filter(email=email.value).first()
        return user_to_domain(record) if record else None

    def add(self, user: User, password: str) -> None:
        record = UserRecord(id=user.id, created_at=user.created_at, **user_fields(user))
        record.set_password(password)
        record.save(force_insert=True)
        # auto_now_add overrides the value on insert; keep the domain's timestamp.
        UserRecord.objects.filter(pk=user.id).update(created_at=user.created_at)

    def save(self, user: User) -> None:
        UserRecord.objects.filter(pk=user.id).update(**user_fields(user))


class DjangoInvitationRepository:
    def get_by_token_hash(self, token_hash: str) -> Invitation | None:
        # Lock the row: concurrent accepts of one invitation run one after the other.
        record = InvitationRecord.objects.select_for_update().filter(token_hash=token_hash).first()
        return invitation_to_domain(record) if record else None

    def add(self, invitation: Invitation) -> None:
        InvitationRecord.objects.create(id=invitation.id, **invitation_fields(invitation))

    def save(self, invitation: Invitation) -> None:
        InvitationRecord.objects.filter(pk=invitation.id).update(**invitation_fields(invitation))


class SystemClock:
    def now(self) -> datetime:
        return timezone.now()
