"""Base error for business-rule violations. The API layer maps `code` to a translated message."""

from typing import ClassVar


class DomainError(Exception):
    code: ClassVar[str] = "domain_error"
    http_status: ClassVar[int] = 400
    # Whether the request's transaction is rolled back. Errors that must leave a trace
    # (e.g. failed sign-in attempts counted for lockout) set this to False.
    rollback: ClassVar[bool] = True


class InvalidValue(DomainError):
    code = "invalid_value"


class CurrencyMismatch(DomainError):
    code = "currency_mismatch"


class NotAllowed(DomainError):
    """The actor may not do this. Reported as not found so nothing's existence leaks."""

    code = "not_found"
    http_status = 404
