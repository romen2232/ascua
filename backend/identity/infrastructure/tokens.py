"""Short-lived signed tokens for multi-step identity flows, and JWT session tokens."""

from uuid import UUID

from django.core import signing
from rest_framework_simplejwt.tokens import RefreshToken

from identity.domain.errors import EnrolmentInvalid, MfaInvalid
from identity.infrastructure.models import UserRecord
from shared_kernel.domain.errors import DomainError

ENROLMENT_MAX_AGE_SECONDS = 15 * 60
MFA_MAX_AGE_SECONDS = 5 * 60


class _SignedUserTokens:
    salt: str
    max_age: int
    error: type[DomainError]

    def issue(self, user_id: UUID) -> str:
        return signing.dumps(str(user_id), salt=self.salt)

    def read(self, token: str) -> UUID:
        try:
            return UUID(signing.loads(token, salt=self.salt, max_age=self.max_age))
        except (signing.BadSignature, ValueError) as exc:
            raise self.error from exc


class SignedEnrolmentTokens(_SignedUserTokens):
    salt = "ascua.identity.enrolment"
    max_age = ENROLMENT_MAX_AGE_SECONDS
    error = EnrolmentInvalid


class SignedMfaTokens(_SignedUserTokens):
    salt = "ascua.identity.mfa"
    max_age = MFA_MAX_AGE_SECONDS
    error = MfaInvalid


def issue_session(user_id: UUID) -> tuple[str, str]:
    """Return (access, refresh) JWTs for a fully signed-in user."""
    refresh = RefreshToken.for_user(UserRecord.objects.get(pk=user_id))
    return str(refresh.access_token), str(refresh)
