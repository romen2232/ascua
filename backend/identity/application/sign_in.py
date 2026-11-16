"""Two-step sign-in: password first, then a TOTP code."""

from dataclasses import dataclass
from uuid import UUID

from identity.application.sign_up import TotpEnrolment
from identity.domain.email import Email, InvalidEmail
from identity.domain.errors import InvalidCredentials, InvalidTotpCode
from identity.domain.ports import (
    CredentialChecker,
    EnrolmentTokens,
    MfaTokens,
    TotpPort,
    UserRepository,
)


@dataclass(frozen=True)
class SignInDeps:
    users: UserRepository
    credentials: CredentialChecker
    totp: TotpPort
    mfa: MfaTokens
    enrolment: EnrolmentTokens


@dataclass(frozen=True)
class MfaRequired:
    mfa_token: str


def start_sign_in(email: str, password: str, deps: SignInDeps) -> MfaRequired | TotpEnrolment:
    """Check the password. Then either ask for the TOTP code, or, if the user never finished
    setting up TOTP, start a fresh enrolment so the account can't be stranded."""
    try:
        normalised = Email(email)
    except InvalidEmail as exc:
        raise InvalidCredentials from exc
    user_id = deps.credentials.check(normalised, password)
    if user_id is None:
        raise InvalidCredentials
    if not deps.users.get(user_id).totp_confirmed:
        return TotpEnrolment(
            user_id=user_id,
            provisioning_uri=deps.totp.create_device(user_id),
            enrolment_token=deps.enrolment.issue(user_id),
        )
    return MfaRequired(deps.mfa.issue(user_id))


def finish_sign_in(mfa_token: str, code: str, deps: SignInDeps) -> UUID:
    """Check the TOTP code and return the signed-in user's id."""
    user_id = deps.mfa.read(mfa_token)
    if not deps.totp.verify(user_id, code):
        raise InvalidTotpCode
    return user_id
