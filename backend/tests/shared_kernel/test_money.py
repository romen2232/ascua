import pytest
from hypothesis import given
from hypothesis import strategies as st

from shared_kernel.domain.basis_points import BasisPoints
from shared_kernel.domain.errors import CurrencyMismatch, InvalidValue
from shared_kernel.domain.money import Money


def test_allocate_sums_exactly():
    parts = Money(100).allocate([BasisPoints(3333), BasisPoints(3333), BasisPoints(3334)])
    assert parts == [Money(33), Money(33), Money(34)]


def test_allocate_ties_go_to_earliest_index():
    assert Money(100).allocate([BasisPoints(1), BasisPoints(1), BasisPoints(1)]) == [
        Money(34),
        Money(33),
        Money(33),
    ]


@given(
    cents=st.integers(-(10**12), 10**12),
    shares=st.lists(st.integers(1, 10000), min_size=1, max_size=6),
)
def test_allocate_never_loses_a_cent(cents, shares):
    parts = Money(cents).allocate([BasisPoints(s) for s in shares])
    assert sum(p.cents for p in parts) == cents


def test_allocate_rejects_all_zero_shares():
    with pytest.raises(InvalidValue):
        Money(100).allocate([BasisPoints(0)])


def test_money_rejects_float():
    with pytest.raises(InvalidValue):
        Money(1.5)  # type: ignore[arg-type]


def test_money_rejects_bool():
    with pytest.raises(InvalidValue):
        Money(True)


def test_money_arithmetic():
    assert Money(150) + Money(50) == Money(200)
    assert Money(150) - Money(200) == Money(-50)
    assert -Money(5) == Money(-5)
    assert Money(5) * 3 == Money(15)
    assert Money.zero() == Money(0)


def test_adding_different_currencies_raises():
    with pytest.raises(CurrencyMismatch):
        Money(1, "EUR") + Money(1, "USD")


def test_errors_carry_a_code():
    with pytest.raises(CurrencyMismatch) as exc:
        Money(1, "EUR") - Money(1, "USD")
    assert exc.value.code == "currency_mismatch"
