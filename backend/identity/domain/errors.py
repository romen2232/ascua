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
