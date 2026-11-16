from shared_kernel.domain.errors import DomainError


class EmailTaken(DomainError):
    code = "email_taken"
    http_status = 409


class WeakPassword(DomainError):
    code = "weak_password"


class InvalidTotpCode(DomainError):
    code = "invalid_totp_code"


class EnrolmentInvalid(DomainError):
    code = "enrolment_invalid"


class InvalidCredentials(DomainError):
    """Same error for an unknown email and a wrong password."""

    code = "invalid_credentials"
    rollback = False  # keep the failed attempt recorded for lockout


class TotpNotEnrolled(DomainError):
    code = "totp_not_enrolled"


class LockedOut(DomainError):
    code = "locked_out"
    http_status = 429
    rollback = False  # the attempt that triggered the lock must stay recorded


class MfaInvalid(DomainError):
    code = "mfa_invalid"
