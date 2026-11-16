"""An email address, normalised so the same person can never register twice."""

from dataclasses import dataclass

from shared_kernel.domain.errors import DomainError


class InvalidEmail(DomainError):
    code = "invalid_email"


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalised = self.value.strip().lower()
        local, sep, domain = normalised.partition("@")
        if (
            not sep
            or not local
            or not domain
            or "@" in domain
            or any(c.isspace() for c in normalised)
        ):
            raise InvalidEmail(f"Not an email address: {self.value!r}")
        object.__setattr__(self, "value", normalised)

    def __str__(self) -> str:
        return self.value
