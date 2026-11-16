"""Money as integer cents. Floats never enter the domain."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from shared_kernel.domain.errors import CurrencyMismatch, InvalidValue

if TYPE_CHECKING:
    from shared_kernel.domain.basis_points import BasisPoints


@dataclass(frozen=True, slots=True)
class Money:
    cents: int
    currency: str = "EUR"

    def __post_init__(self) -> None:
        if type(self.cents) is not int:
            raise InvalidValue(f"Money needs integer cents, got {type(self.cents).__name__}")
        if len(self.currency) != 3 or not self.currency.isupper():
            raise InvalidValue(f"Invalid ISO 4217 currency: {self.currency!r}")

    @classmethod
    def zero(cls, currency: str = "EUR") -> Money:
        return cls(0, currency)

    def _same_currency(self, other: Money) -> None:
        if other.currency != self.currency:
            raise CurrencyMismatch(f"{self.currency} vs {other.currency}")

    def __add__(self, other: Money) -> Money:
        self._same_currency(other)
        return Money(self.cents + other.cents, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._same_currency(other)
        return Money(self.cents - other.cents, self.currency)

    def __neg__(self) -> Money:
        return Money(-self.cents, self.currency)

    def __mul__(self, factor: int) -> Money:
        if type(factor) is not int:
            raise InvalidValue("Money can only be multiplied by an integer")
        return Money(self.cents * factor, self.currency)

    def allocate(self, shares: Sequence[BasisPoints]) -> list[Money]:
        """Split proportionally to `shares` (largest remainder); parts always sum to self."""
        weights = [s.value for s in shares]
        total = sum(weights)
        if total == 0:
            raise InvalidValue("Cannot allocate over shares that sum to zero")
        floors = [self.cents * w // total for w in weights]
        remainders = [self.cents * w % total for w in weights]
        leftover = self.cents - sum(floors)
        order = sorted(range(len(weights)), key=lambda i: (-remainders[i], i))
        for i in order[:leftover]:
            floors[i] += 1
        return [Money(c, self.currency) for c in floors]
