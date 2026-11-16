"""ORM record <-> domain entity. No business rules here."""

from typing import cast

from identity.domain.email import Email
from identity.domain.invitation import Invitation
from identity.domain.user import Locale, User
from identity.infrastructure.models import InvitationRecord, UserRecord


def user_to_domain(r: UserRecord) -> User:
    return User(
        id=r.id,
        email=Email(r.email),
        display_name=r.display_name,
        locale=cast(Locale, r.locale),
        is_admin=r.is_admin,
        totp_confirmed=r.totp_confirmed,
        created_at=r.created_at,
    )


def user_fields(u: User) -> dict[str, object]:
    return {
        "email": u.email.value,
        "display_name": u.display_name,
        "locale": u.locale,
        "is_admin": u.is_admin,
        "totp_confirmed": u.totp_confirmed,
    }


def invitation_to_domain(r: InvitationRecord) -> Invitation:
    return Invitation(
        id=r.id,
        email=Email(r.email),
        token_hash=r.token_hash,
        invited_by=r.invited_by_id,
        expires_at=r.expires_at,
        used_at=r.used_at,
    )


def invitation_fields(i: Invitation) -> dict[str, object]:
    return {
        "email": i.email.value,
        "token_hash": i.token_hash,
        "invited_by_id": i.invited_by,
        "expires_at": i.expires_at,
        "used_at": i.used_at,
    }
