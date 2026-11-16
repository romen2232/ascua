"""Two-step sign-in: password first, then a TOTP code."""

from dataclasses import dataclass
from uuid import UUID

from identity.domain.email import Email, InvalidEmail
from identity.domain.errors import InvalidCredentials, InvalidTotpCode, TotpNotEnrolled
from identity.domain.ports import CredentialChecker, MfaTokens, TotpPort, UserRepository


@dataclass(frozen=True)
class SignInDeps:
    users: UserRepository
    credentials: CredentialChecker
    totp: TotpPort
    mfa: MfaTokens


def start_sign_in(email: str, password: str, deps: SignInDeps) -> str:
    """Check the password and return a short-lived token for the TOTP step."""
    try:
        normalised = Email(email)
    except InvalidEmail as exc:
        raise InvalidCredentials from exc
    user_id = deps.credentials.check(normalised, password)
    if user_id is None:
        raise InvalidCredentials
    if not deps.users.get(user_id).totp_confirmed:
        raise TotpNotEnrolled
    return deps.mfa.issue(user_id)


def finish_sign_in(mfa_token: str, code: str, deps: SignInDeps) -> UUID:
    """Check the TOTP code and return the signed-in user's id."""
    user_id = deps.mfa.read(mfa_token)
    if not deps.totp.verify(user_id, code):
        raise InvalidTotpCode
    return user_id
