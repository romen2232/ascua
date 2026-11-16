from dataclasses import dataclass

from identity.domain.ports import (
    Clock,
    EnrolmentTokens,
    InvitationRepository,
    TotpPort,
    UserRepository,
)


@dataclass(frozen=True)
class SignUpDeps:
    users: UserRepository
    invitations: InvitationRepository
    clock: Clock
    totp: TotpPort
    enrolment: EnrolmentTokens
