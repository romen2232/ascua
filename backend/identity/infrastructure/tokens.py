"""Short-lived signed tokens for multi-step identity flows."""

from uuid import UUID

from django.core import signing

from identity.domain.errors import EnrolmentInvalid

ENROLMENT_MAX_AGE_SECONDS = 15 * 60


class SignedEnrolmentTokens:
    salt = "ascua.identity.enrolment"

    def issue(self, user_id: UUID) -> str:
        return signing.dumps(str(user_id), salt=self.salt)

    def read(self, token: str) -> UUID:
        try:
            return UUID(signing.loads(token, salt=self.salt, max_age=ENROLMENT_MAX_AGE_SECONDS))
        except (signing.BadSignature, ValueError) as exc:
            raise EnrolmentInvalid from exc
