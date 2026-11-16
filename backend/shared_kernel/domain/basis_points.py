"""Shares and percentages as integer basis points: 10000 = 100 %."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation

from shared_kernel.domain.errors import InvalidValue
from shared_kernel.domain.money import Money

FULL = 10000


@dataclass(frozen=True, slots=True)
class BasisPoints:
    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int or not 0 <= self.value <= FULL:
            raise InvalidValue(f"Basis points must be an integer in 0..{FULL}")

    @classmethod
    def from_percent_str(cls, text: str) -> BasisPoints:
        try:
            scaled = Decimal(text) * 100
        except InvalidOperation as exc:
            raise InvalidValue(f"Not a percentage: {text!r}") from exc
        if scaled != scaled.to_integral_value():
            raise InvalidValue(f"More than two decimals: {text!r}")
        return cls(int(scaled))

    def of(self, money: Money) -> Money:
        """This share of `money`, rounded half to even to the cent."""
        exact = Decimal(money.cents) * self.value / FULL
        return Money(int(exact.to_integral_value(rounding=ROUND_HALF_EVEN)), money.currency)
