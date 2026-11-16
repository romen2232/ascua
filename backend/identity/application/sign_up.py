"""Sign-up by invitation, followed by mandatory TOTP enrolment."""

import uuid
from dataclasses import dataclass
from typing import cast
from uuid import UUID

from identity.application.deps import SignUpDeps
from identity.domain.errors import EmailTaken, EnrolmentInvalid, InvalidTotpCode, WeakPassword
from identity.domain.invitation import InvitationInvalid, hash_token
from identity.domain.user import Locale, User
from shared_kernel.domain.errors import InvalidValue

__all__ = ["SignUpDeps", "TotpEnrolment", "accept_invitation", "confirm_totp"]

MIN_PASSWORD_LENGTH = 12
LOCALES = ("es", "en")


@dataclass(frozen=True)
class TotpEnrolment:
    user_id: UUID
    provisioning_uri: str
    enrolment_token: str


def accept_invitation(
    raw_token: str, display_name: str, password: str, locale: str, deps: SignUpDeps
) -> TotpEnrolment:
    invitation = deps.invitations.get_by_token_hash(hash_token(raw_token))
    if invitation is None:
        raise InvitationInvalid
    name = display_name.strip()
    if not name or len(name) > 100:
        raise InvalidValue("display name")
    if locale not in LOCALES:
        raise InvalidValue("locale")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise WeakPassword

    now = deps.clock.now()
    invitation.accept(raw_token, now)  # raises if used or expired
    if deps.users.get_by_email(invitation.email) is not None:
        raise EmailTaken

    user = User(
        id=uuid.uuid4(),
        email=invitation.email,
        display_name=name,
        locale=cast(Locale, locale),
        is_admin=False,
        totp_confirmed=False,
        created_at=now,
    )
    deps.users.add(user, password)
    deps.invitations.save(invitation)
    return TotpEnrolment(
        user_id=user.id,
        provisioning_uri=deps.totp.create_device(user.id),
        enrolment_token=deps.enrolment.issue(user.id),
    )


def confirm_totp(enrolment_token: str, code: str, deps: SignUpDeps) -> None:
    user = deps.users.get(deps.enrolment.read(enrolment_token))
    if user.totp_confirmed:
        raise EnrolmentInvalid
    if not deps.totp.verify(user.id, code):
        raise InvalidTotpCode
    user.totp_confirmed = True
    deps.users.save(user)
