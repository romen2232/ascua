"""Base error for business-rule violations. The API layer maps `code` to a translated message."""

from typing import ClassVar


class DomainError(Exception):
    code: ClassVar[str] = "domain_error"
    http_status: ClassVar[int] = 400


class InvalidValue(DomainError):
    code = "invalid_value"


class CurrencyMismatch(DomainError):
    code = "currency_mismatch"
